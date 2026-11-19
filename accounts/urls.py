from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.RoleLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('direction/', views.DirectionDashboard.as_view(), name='direction_dashboard'),
    path('teacher/', views.TeacherDashboard.as_view(), name='teacher_dashboard'),
    path('student/', views.StudentDashboard.as_view(), name='student_dashboard'),
    path('direction/results/', views.ClassResultsView.as_view(), name='class_results'),
    path('direction/results/export/', views.ExportClassResultsView.as_view(), name='export_class_results'),
    path('parent/', views.ParentDashboard.as_view(), name='parent_dashboard'),
    


]