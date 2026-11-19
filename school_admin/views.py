from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from academics.models import SchoolClass
from accounts.mixins import RoleRequiredMixin
from accounts.models import User
from people.models import Employee, Enrollment, Parent, Student, TeachingAssignment

from .forms import (
    AssignTeacherForm, EmployeeCreateForm, EmployeeEditForm, EnrollForm,
    ParentCreateForm, ParentEditForm, StudentCreateForm, StudentEditForm,
)

class DirectionOnly(RoleRequiredMixin):
    allowed_roles = [User.Role.DIRECTION]


class BaseList(DirectionOnly, ListView):
    template_name = 'school_admin/list.html'
    paginate_by = 20
    title = ''
    headers = []
    create_url = ''
    edit_url = ''
    extra_url = ''
    extra_label = ''

    def get_q(self):
        return self.request.GET.get('q', '').strip()

    def row(self, obj):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['headers'] = self.headers
        context['create_url'] = self.create_url
        context['edit_url'] = self.edit_url
        context['extra_url'] = self.extra_url
        context['extra_label'] = self.extra_label
        context['q'] = self.get_q()
        context['rows'] = [(obj, self.row(obj)) for obj in context['object_list']]
        return context


class StudentList(BaseList):
    title = 'Students'
    headers = ['Number', 'Name', 'Username']
    create_url = 'student_create'
    edit_url = 'student_edit'

    def get_queryset(self):
        qs = Student.objects.select_related('user').order_by('user__last_name', 'user__first_name')
        q = self.get_q()
        if q:
            qs = qs.filter(
                Q(student_number__icontains=q) | Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q) | Q(user__username__icontains=q)
            )
        return qs

    def row(self, s):
        return [s.student_number, s.user.get_full_name() or s.user.username, s.user.username]


class EmployeeList(BaseList):
    title = 'Employees'
    headers = ['Name', 'Position', 'Role', 'Username']
    create_url = 'employee_create'
    edit_url = 'employee_edit'

    def get_queryset(self):
        qs = Employee.objects.select_related('user').order_by('user__last_name', 'user__first_name')
        q = self.get_q()
        if q:
            qs = qs.filter(
                Q(position__icontains=q) | Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q) | Q(user__username__icontains=q)
            )
        return qs

    def row(self, e):
        return [e.user.get_full_name() or e.user.username, e.position, e.user.get_role_display(), e.user.username]


class ClassList(BaseList):
    title = 'Classes'
    headers = ['Class', 'Level', 'Academic year']
    create_url = 'class_create'
    edit_url = 'class_edit'
    extra_url = 'class_detail'
    extra_label = 'Students and teachers'

    def get_queryset(self):
        qs = SchoolClass.objects.select_related('level', 'academic_year').order_by('-academic_year__start_date', 'name')
        q = self.get_q()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(level__name__icontains=q) | Q(academic_year__name__icontains=q)
            )
        return qs

    def row(self, c):
        return [c.name, c.level.name, c.academic_year.name]


class FormPage(DirectionOnly):
    template_name = 'school_admin/form.html'
    title = ''
    list_name = ''

    def get_success_url(self):
        return reverse(self.list_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['back_url'] = reverse(self.list_name)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Saved.')
        return super().form_valid(form)


class StudentCreate(FormPage, CreateView):
    model = Student
    form_class = StudentCreateForm
    title = 'New student'
    list_name = 'student_list'


class StudentEdit(FormPage, UpdateView):
    model = Student
    form_class = StudentEditForm
    title = 'Edit student'
    list_name = 'student_list'


class EmployeeCreate(FormPage, CreateView):
    model = Employee
    form_class = EmployeeCreateForm
    title = 'New employee'
    list_name = 'employee_list'


class EmployeeEdit(FormPage, UpdateView):
    model = Employee
    form_class = EmployeeEditForm
    title = 'Edit employee'
    list_name = 'employee_list'


class ClassCreate(FormPage, CreateView):
    model = SchoolClass
    fields = ['level', 'academic_year', 'name']
    title = 'New class'
    list_name = 'class_list'


class ClassEdit(FormPage, UpdateView):
    model = SchoolClass
    fields = ['level', 'academic_year', 'name']
    title = 'Edit class'
    list_name = 'class_list'



class ClassDetailView(DirectionOnly, TemplateView):
    template_name = 'school_admin/class_detail.html'

    def get_school_class(self):
        return get_object_or_404(SchoolClass.objects.select_related('level', 'academic_year'), pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school_class = self.get_school_class()
        context['school_class'] = school_class
        context['enroll_form'] = kwargs.get('enroll_form') or EnrollForm(school_class=school_class)
        context['assign_form'] = kwargs.get('assign_form') or AssignTeacherForm(school_class=school_class)
        context['enrollments'] = (
            Enrollment.objects.filter(school_class=school_class)
            .select_related('student__user')
            .order_by('student__user__last_name', 'student__user__first_name')
        )
        context['assignments'] = (
            TeachingAssignment.objects.filter(school_class=school_class)
            .select_related('teacher__user', 'subject')
            .order_by('subject__name')
        )
        return context

    def post(self, request, *args, **kwargs):
        school_class = self.get_school_class()
        action = request.POST.get('action')

        if action == 'enroll':
            form = EnrollForm(request.POST, school_class=school_class)
            if form.is_valid():
                students = form.cleaned_data['students']
                Enrollment.objects.bulk_create(
                    [Enrollment(student=s, school_class=school_class) for s in students]
                )
                messages.success(request, '%d student(s) added to the class.' % len(students))
                return redirect('class_detail', pk=school_class.pk)
            return self.render_to_response(self.get_context_data(enroll_form=form))

        if action == 'assign':
            form = AssignTeacherForm(request.POST, school_class=school_class)
            if form.is_valid():
                TeachingAssignment.objects.create(
                    teacher=form.cleaned_data['teacher'],
                    subject=form.cleaned_data['subject'],
                    school_class=school_class,
                )
                messages.success(request, 'The teacher was assigned.')
                return redirect('class_detail', pk=school_class.pk)
            return self.render_to_response(self.get_context_data(assign_form=form))

        return redirect('class_detail', pk=school_class.pk)


class EnrollmentRemove(DirectionOnly, View):
    def post(self, request, pk):
        enrollment = get_object_or_404(Enrollment, pk=pk)
        class_id = enrollment.school_class_id
        enrollment.delete()
        messages.success(request, 'The student was removed from the class.')
        return redirect('class_detail', pk=class_id)


class AssignmentRemove(DirectionOnly, View):
    def post(self, request, pk):
        assignment = get_object_or_404(TeachingAssignment, pk=pk)
        class_id = assignment.school_class_id
        assignment.delete()
        messages.success(request, 'The teacher was removed from the subject.')
        return redirect('class_detail', pk=class_id)


class ParentList(BaseList):
    title = 'Parents'
    headers = ['Name', 'Username', 'Phone', 'Children']
    create_url = 'parent_create'
    edit_url = 'parent_edit'

    def get_queryset(self):
        qs = (
            Parent.objects
            .select_related('user')
            .prefetch_related('children__user')
            .order_by('user__last_name', 'user__first_name')
        )
        q = self.get_q()
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q)
                | Q(user__username__icontains=q) | Q(phone__icontains=q)
                | Q(children__user__first_name__icontains=q) | Q(children__user__last_name__icontains=q)
            ).distinct()
        return qs

    def row(self, p):
        children = ', '.join(c.user.get_full_name() or c.user.username for c in p.children.all())
        return [p.user.get_full_name() or p.user.username, p.user.username, p.phone or '-', children or '-']


class ParentCreate(FormPage, CreateView):
    model = Parent
    form_class = ParentCreateForm
    title = 'New parent'
    list_name = 'parent_list'


class ParentEdit(FormPage, UpdateView):
    model = Parent
    form_class = ParentEditForm
    title = 'Edit parent'
    list_name = 'parent_list'


