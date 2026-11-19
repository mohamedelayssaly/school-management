from django import forms

from academics.models import SchoolClass, Subject
from accounts.models import User
from people.models import Employee, Enrollment, Parent, Student, TeachingAssignment

def date_widget():
    return forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')


def create_user(data, role):
    user = User(
        username=data['username'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=role,
    )
    user.set_password(data['password'])
    user.save()
    return user


def check_username(username):
    if User.objects.filter(username=username).exists():
        raise forms.ValidationError('This username is already used.')
    return username


class StudentCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    school_class = forms.ModelChoiceField(
        queryset=SchoolClass.objects.select_related('academic_year'),
        required=False,
        label='Class (optional)',
    )

    class Meta:
        model = Student
        fields = ['student_number', 'birth_date']
        widgets = {'birth_date': date_widget()}

    field_order = ['username', 'first_name', 'last_name', 'password', 'student_number', 'birth_date', 'school_class']

    def clean_username(self):
        return check_username(self.cleaned_data['username'])

    def save(self, commit=True):
        student = super().save(commit=False)
        student.user = create_user(self.cleaned_data, User.Role.STUDENT)
        if commit:
            student.save()
            school_class = self.cleaned_data.get('school_class')
            if school_class:
                Enrollment.objects.create(student=student, school_class=school_class)
        return student


class StudentEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = Student
        fields = ['student_number', 'birth_date']
        widgets = {'birth_date': date_widget()}

    field_order = ['first_name', 'last_name', 'student_number', 'birth_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        student = super().save(commit=commit)
        user = student.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return student


class EmployeeCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[('teacher', 'Teacher'), ('direction', 'Direction')])

    class Meta:
        model = Employee
        fields = ['position', 'hire_date']
        widgets = {'hire_date': date_widget()}

    field_order = ['username', 'first_name', 'last_name', 'password', 'role', 'position', 'hire_date']

    def clean_username(self):
        return check_username(self.cleaned_data['username'])

    def save(self, commit=True):
        employee = super().save(commit=False)
        employee.user = create_user(self.cleaned_data, self.cleaned_data['role'])
        if commit:
            employee.save()
        return employee


class EmployeeEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = Employee
        fields = ['position', 'hire_date']
        widgets = {'hire_date': date_widget()}

    field_order = ['first_name', 'last_name', 'position', 'hire_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        employee = super().save(commit=commit)
        user = employee.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return employee



class EnrollForm(forms.Form):
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label='Students to add',
    )

    def __init__(self, *args, school_class, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['students'].queryset = (
            Student.objects
            .exclude(enrollment__school_class__academic_year=school_class.academic_year)
            .select_related('user')
            .order_by('user__last_name', 'user__first_name')
        )


class AssignTeacherForm(forms.Form):
    teacher = forms.ModelChoiceField(queryset=Employee.objects.none())
    subject = forms.ModelChoiceField(queryset=Subject.objects.all())

    def __init__(self, *args, school_class, **kwargs):
        super().__init__(*args, **kwargs)
        self.school_class = school_class
        self.fields['teacher'].queryset = (
            Employee.objects
            .filter(user__role=User.Role.TEACHER)
            .select_related('user')
            .order_by('user__last_name', 'user__first_name')
        )

    def clean(self):
        cleaned = super().clean()
        subject = cleaned.get('subject')
        if subject and TeachingAssignment.objects.filter(school_class=self.school_class, subject=subject).exists():
            raise forms.ValidationError('This subject already has a teacher in this class. Remove the current assignment first.')
        return cleaned


def children_field():
    return forms.ModelMultipleChoiceField(
        queryset=Student.objects.select_related('user').order_by('user__last_name', 'user__first_name'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Children (students)',
    )


class ParentCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    children = children_field()

    class Meta:
        model = Parent
        fields = ['phone', 'children']

    field_order = ['username', 'first_name', 'last_name', 'password', 'phone', 'children']

    def clean_username(self):
        return check_username(self.cleaned_data['username'])

    def save(self, commit=True):
        parent = super().save(commit=False)
        parent.user = create_user(self.cleaned_data, User.Role.PARENT)
        if commit:
            parent.save()
            self.save_m2m()
        return parent



class ParentEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    children = children_field()

    class Meta:
        model = Parent
        fields = ['phone', 'children']

    field_order = ['first_name', 'last_name', 'phone', 'children']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        parent = super().save(commit=commit)
        user = parent.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return parent



