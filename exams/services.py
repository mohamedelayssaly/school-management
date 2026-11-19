from collections import defaultdict
from decimal import Decimal

from .models import Grade


def student_report(student, term=None, year=None):
    """Returns (rows, overall). Each row has subject, coefficient and average out of 20."""
    grades = (
        Grade.objects
        .filter(student=student, score__isnull=False, is_absent=False)
        .select_related('exam__subject')
    )
    if term:
        grades = grades.filter(exam__term=term)
    if year:
        grades = grades.filter(exam__term__academic_year=year)

    by_subject = defaultdict(list)
    for g in grades:
        by_subject[g.exam.subject].append(g.score / g.exam.max_score * 20)

    rows = []
    total = Decimal(0)
    weight = Decimal(0)
    for subject, scores in by_subject.items():
        average = sum(scores) / len(scores)
        rows.append({'subject': subject, 'coefficient': subject.coefficient, 'average': average})
        total += average * subject.coefficient
        weight += subject.coefficient

    overall = total / weight if weight else None
    return rows, overall


def class_ranking(school_class, term=None):
    """Returns a list of dicts (student, average, rank), best average first."""
    results = []
    for enrollment in school_class.enrollment_set.select_related('student__user'):
        _, overall = student_report(enrollment.student, term=term)
        results.append({'student': enrollment.student, 'average': overall})
    results.sort(key=lambda r: (r['average'] is None, -(r['average'] or 0)))
    for position, result in enumerate(results, start=1):
        result['rank'] = position
    return results