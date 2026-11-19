from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from django.http import HttpResponse
from django.views import View
from openpyxl import Workbook
from openpyxl.styles import Font

from academics.models import SchoolClass , Term
from exams.models import Exam, Grade
from exams.services import class_ranking, student_report
from people.models import Employee, Parent, Student, TeachingAssignment

from .mixins import RoleRequiredMixin
from .models import User
from .student_data import student_overview


class RoleLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


def home(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    if user.is_superuser or user.role == User.Role.DIRECTION:
        return redirect('direction_dashboard')
    if user.role == User.Role.TEACHER:
        return redirect('teacher_dashboard')
    if user.role == User.Role.STUDENT:
        return redirect('student_dashboard')
    if user.role == User.Role.PARENT:
        return redirect('parent_dashboard')
    return redirect('login')


class DirectionDashboard(RoleRequiredMixin, TemplateView):
    template_name = 'accounts/direction_dashboard.html'
    allowed_roles = [User.Role.DIRECTION]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students_count'] = Student.objects.count()
        context['employees_count'] = Employee.objects.count()
        context['classes_count'] = SchoolClass.objects.count()
        context['exams_count'] = Exam.objects.count()
        return context


class TeacherDashboard(RoleRequiredMixin, TemplateView):
    template_name = 'accounts/teacher_dashboard.html'
    allowed_roles = [User.Role.TEACHER]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignments'] = (
            TeachingAssignment.objects
            .filter(teacher__user=self.request.user)
            .select_related('subject', 'school_class')
        )
        return context


class StudentDashboard(RoleRequiredMixin, TemplateView):
    template_name = 'accounts/student_dashboard.html'
    allowed_roles = [User.Role.STUDENT]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = Student.objects.filter(user=self.request.user).first()
        context['overview'] = student_overview(student) if student else None
        return context

class ClassResultsView(RoleRequiredMixin, TemplateView):
    template_name = 'accounts/class_results.html'
    allowed_roles = [User.Role.DIRECTION]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = SchoolClass.objects.select_related('academic_year')
        context['terms'] = Term.objects.select_related('academic_year')
        class_id = self.request.GET.get('class')
        term_id = self.request.GET.get('term')
        if class_id and term_id:
            school_class = get_object_or_404(SchoolClass, pk=class_id)
            term = get_object_or_404(Term, pk=term_id)
            context['selected_class'] = school_class
            context['selected_term'] = term
            context['ranking'] = class_ranking(school_class, term)
        return context



PASS_MARK = 10


class ExportClassResultsView(RoleRequiredMixin, View):
    allowed_roles = [User.Role.DIRECTION]

    def get(self, request):
        school_class = get_object_or_404(SchoolClass, pk=request.GET.get('class'))
        term = get_object_or_404(Term, pk=request.GET.get('term'))

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Results'
        sheet.append(['Rank', 'Student number', 'Student', 'Average / 20', 'Result'])
        for cell in sheet[1]:
            cell.font = Font(bold=True)

        for r in class_ranking(school_class, term):
            average = float(r['average']) if r['average'] is not None else None
            result = '' if average is None else ('Pass' if average >= PASS_MARK else 'Fail')
            sheet.append([
                r['rank'],
                r['student'].student_number,
                r['student'].user.get_full_name() or r['student'].user.username,
                round(average, 2) if average is not None else None,
                result,
            ])

        for column, width in zip('ABCDE', [8, 18, 30, 14, 10]):
            sheet.column_dimensions[column].width = width

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=results_class%s_term%s.xlsx' % (school_class.pk, term.pk)
        workbook.save(response)
        return response



class ParentDashboard(RoleRequiredMixin, TemplateView):
    template_name = 'accounts/parent_dashboard.html'
    allowed_roles = [User.Role.PARENT]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent = Parent.objects.filter(user=self.request.user).first()
        children = parent.children.select_related('user') if parent else []
        context['overviews'] = [student_overview(child) for child in children]
        return context








