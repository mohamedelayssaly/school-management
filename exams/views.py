from io import BytesIO
from school_settings.models import SchoolProfile
from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from academics.models import Term
from people.models import Student

from .services import student_report

from decimal import Decimal, InvalidOperation
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from people.models import Enrollment, TeachingAssignment

from .forms import ExamForm
from .models import Exam, Grade


def teacher_only(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.user.role != User.Role.TEACHER:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return login_required(wrapper)


def own_assignment_or_404(request, pk):
    return get_object_or_404(
        TeachingAssignment.objects.select_related('subject', 'school_class'),
        pk=pk, teacher__user=request.user,
    )


@teacher_only
def assignment_detail(request, pk):
    assignment = own_assignment_or_404(request, pk)
    exams = (
        Exam.objects
        .filter(subject=assignment.subject, school_class=assignment.school_class)
        .select_related('term')
        .order_by('-date')
    )
    return render(request, 'exams/assignment_detail.html', {'assignment': assignment, 'exams': exams})


@teacher_only
def exam_create(request, assignment_id):
    assignment = own_assignment_or_404(request, assignment_id)
    form = ExamForm(request.POST or None, assignment=assignment)
    if request.method == 'POST' and form.is_valid():
        exam = form.save(commit=False)
        exam.subject = assignment.subject
        exam.school_class = assignment.school_class
        exam.save()
        messages.success(request, 'Exam created. You can enter the grades now.')
        return redirect('grade_entry', exam_id=exam.pk)
    return render(request, 'exams/exam_form.html', {'form': form, 'assignment': assignment})


@teacher_only
def grade_entry(request, exam_id):
    exam = get_object_or_404(Exam.objects.select_related('subject', 'school_class', 'term'), pk=exam_id)
    assignment = TeachingAssignment.objects.filter(
        teacher__user=request.user, subject=exam.subject, school_class=exam.school_class,
    ).first()
    if assignment is None:
        raise PermissionDenied

    enrollments = (
        Enrollment.objects
        .filter(school_class=exam.school_class)
        .select_related('student__user')
        .order_by('student__user__last_name', 'student__user__first_name')
    )
    existing = {g.student_id: g for g in exam.grades.all()}
    rows = []
    for enr in enrollments:
        g = existing.get(enr.student_id)
        rows.append({
            'student': enr.student,
            'score': g.score if g and g.score is not None else '',
            'absent': bool(g and g.is_absent),
        })

    if request.method == 'POST':
        valid = True
        to_save = []
        for row in rows:
            sid = row['student'].pk
            absent = ('absent_%s' % sid) in request.POST
            raw = request.POST.get('score_%s' % sid, '').strip().replace(',', '.')
            row['score'], row['absent'] = raw, absent
            score = None
            if raw and not absent:
                try:
                    score = Decimal(raw)
                except InvalidOperation:
                    messages.error(request, 'Invalid score for %s.' % row['student'])
                    valid = False
                    continue
                if not score.is_finite() or not (0 <= score <= exam.max_score):
                    messages.error(request, 'Score for %s must be between 0 and %s.' % (row['student'], exam.max_score))
                    valid = False
                    continue
            to_save.append((row['student'], score, absent))
        if valid:
            for student, score, absent in to_save:
                Grade.objects.update_or_create(
                    exam=exam, student=student,
                    defaults={'score': score, 'is_absent': absent},
                )
            messages.success(request, 'Grades saved.')
            return redirect('assignment_detail', pk=assignment.pk)

    return render(request, 'exams/grade_entry.html', {'exam': exam, 'rows': rows, 'assignment': assignment})



@login_required
def report_card_pdf(request, term_id):
    student = get_object_or_404(Student, user=request.user)
    term = get_object_or_404(Term, pk=term_id)
    rows, overall = student_report(student, term=term)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    y = 800
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(50, 825, SchoolProfile.get().name)
    y -= 30
    pdf.setFont('Helvetica', 12)
    pdf.drawString(50, y, 'Student: %s' % student)
    y -= 40
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(50, y, 'Subject')
    pdf.drawString(300, y, 'Coef.')
    pdf.drawString(380, y, 'Average / 20')
    pdf.setFont('Helvetica', 12)
    for row in rows:
        y -= 22
        pdf.drawString(50, y, row['subject'].name)
        pdf.drawString(300, y, str(row['coefficient']))
        pdf.drawString(380, y, '%.2f' % row['average'])
    y -= 35
    pdf.setFont('Helvetica-Bold', 12)
    if overall is not None:
        pdf.drawString(50, y, 'Term average: %.2f / 20' % overall)
    else:
        pdf.drawString(50, y, 'Term average: -')
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='report_card.pdf')


