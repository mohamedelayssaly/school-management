from datetime import date
from django.db.models import Count
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from academics.models import SchoolClass
from exams.views import teacher_only
from people.models import Enrollment, TeachingAssignment

from .models import Attendance


@teacher_only
def attendance_sheet(request, class_id):
    school_class = get_object_or_404(SchoolClass, pk=class_id)
    if not TeachingAssignment.objects.filter(teacher__user=request.user, school_class=school_class).exists():
        raise PermissionDenied

    try:
        day = date.fromisoformat(request.GET.get('date') or request.POST.get('date') or '')
    except ValueError:
        day = date.today()

    enrollments = (
        Enrollment.objects
        .filter(school_class=school_class)
        .select_related('student__user')
        .order_by('student__user__last_name', 'student__user__first_name')
    )

    if request.method == 'POST':
        for enr in enrollments:
            sid = enr.student_id
            status = request.POST.get('status_%s' % sid, Attendance.Status.PRESENT)
            if status not in Attendance.Status.values:
                status = Attendance.Status.PRESENT
            note = request.POST.get('note_%s' % sid, '').strip()[:200]
            Attendance.objects.update_or_create(
                student=enr.student, date=day,
                defaults={'school_class': school_class, 'status': status, 'note': note},
            )
        messages.success(request, 'Attendance saved.')
        return redirect('%s?date=%s' % (reverse('attendance_sheet', args=[school_class.pk]), day.isoformat()))

    existing = {a.student_id: a for a in Attendance.objects.filter(school_class=school_class, date=day)}
    rows = []
    for enr in enrollments:
        record = existing.get(enr.student_id)
        rows.append({
            'student': enr.student,
            'status': record.status if record else Attendance.Status.PRESENT,
            'note': record.note if record else '',
        })
    return render(request, 'attendance/sheet.html', {
        'school_class': school_class,
        'day': day,
        'rows': rows,
        'statuses': Attendance.Status.choices,
    })


@teacher_only
def class_students(request, class_id):
    school_class = get_object_or_404(SchoolClass.objects.select_related('level', 'academic_year'), pk=class_id)
    assignments = list(
        TeachingAssignment.objects
        .filter(teacher__user=request.user, school_class=school_class)
        .select_related('subject')
    )
    if not assignments:
        raise PermissionDenied

    absences = dict(
        Attendance.objects
        .filter(school_class=school_class, status=Attendance.Status.ABSENT)
        .values_list('student_id')
        .annotate(total=Count('id'))
    )
    enrollments = (
        Enrollment.objects
        .filter(school_class=school_class)
        .select_related('student__user')
        .prefetch_related('student__parents__user')
        .order_by('student__user__last_name', 'student__user__first_name')
    )
    rows = [
        {
            'student': enr.student,
            'parents': list(enr.student.parents.all()),
            'absences': absences.get(enr.student_id, 0),
        }
        for enr in enrollments
    ]
    return render(request, 'attendance/students.html', {
        'school_class': school_class,
        'assignments': assignments,
        'rows': rows,
    })

