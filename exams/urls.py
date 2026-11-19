from django.urls import path

from . import views

urlpatterns = [
    path('teacher/assignment/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('teacher/assignment/<int:assignment_id>/exams/new/', views.exam_create, name='exam_create'),
    path('teacher/exam/<int:exam_id>/grades/', views.grade_entry, name='grade_entry'),
    path('student/report/<int:term_id>/pdf/', views.report_card_pdf, name='report_card_pdf'),
]