from django.urls import path

from . import views

urlpatterns = [
    path('teacher/attendance/<int:class_id>/', views.attendance_sheet, name='attendance_sheet'),
    path('teacher/class/<int:class_id>/students/', views.class_students, name='class_students'),
    


]