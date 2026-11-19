from academics.models import Term
from attendance.models import Attendance
from exams.services import student_report
from people.models import Enrollment, TeachingAssignment


def student_overview(student):
    reports = []
    for term in Term.objects.filter(academic_year__is_current=True):
        rows, overall = student_report(student, term=term)
        reports.append({'term': term, 'rows': rows, 'overall': overall})

    enrollment = (
        Enrollment.objects
        .filter(student=student, school_class__academic_year__is_current=True)
        .select_related('school_class')
        .first()
    )
    school_class = enrollment.school_class if enrollment else None
    teachers = []
    if school_class:
        teachers = (
            TeachingAssignment.objects
            .filter(school_class=school_class)
            .select_related('subject', 'teacher__user')
            .order_by('subject__name')
        )

    records = Attendance.objects.filter(student=student)
    return {
        'student': student,
        'reports': reports,
        'school_class': school_class,
        'teachers': teachers,
        'absence_count': records.filter(status=Attendance.Status.ABSENT).count(),
        'late_count': records.filter(status=Attendance.Status.LATE).count(),
        'recent_attendance': records.exclude(status=Attendance.Status.PRESENT).order_by('-date')[:10],
    }