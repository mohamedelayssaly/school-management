from django.urls import path

from . import views

urlpatterns = [
    path('manage/students/', views.StudentList.as_view(), name='student_list'),
    path('manage/students/new/', views.StudentCreate.as_view(), name='student_create'),
    path('manage/students/<int:pk>/edit/', views.StudentEdit.as_view(), name='student_edit'),
    path('manage/employees/', views.EmployeeList.as_view(), name='employee_list'),
    path('manage/employees/new/', views.EmployeeCreate.as_view(), name='employee_create'),
    path('manage/employees/<int:pk>/edit/', views.EmployeeEdit.as_view(), name='employee_edit'),
    path('manage/classes/', views.ClassList.as_view(), name='class_list'),
    path('manage/classes/new/', views.ClassCreate.as_view(), name='class_create'),
    path('manage/classes/<int:pk>/edit/', views.ClassEdit.as_view(), name='class_edit'),
    path('manage/classes/<int:pk>/', views.ClassDetailView.as_view(), name='class_detail'),
    path('manage/enrollments/<int:pk>/remove/', views.EnrollmentRemove.as_view(), name='enrollment_remove'),
    path('manage/assignments/<int:pk>/remove/', views.AssignmentRemove.as_view(), name='assignment_remove'),
    path('manage/parents/', views.ParentList.as_view(), name='parent_list'),
    path('manage/parents/new/', views.ParentCreate.as_view(), name='parent_create'),
    path('manage/parents/<int:pk>/edit/', views.ParentEdit.as_view(), name='parent_edit'),
]