from django.urls import path
from . import views

urlpatterns = [
    path('lecture/<int:lecture_pk>/submissions/', views.quiz_submissions_list, name='quiz_submissions_list'),
    path('submission/<int:submission_pk>/grade/', views.grade_submission, name='grade_submission'),
    path('student/grades/', views.student_quiz_grades, name='student_quiz_grades'),
    path('student/submission/<int:submission_pk>/', views.student_quiz_detail, name='student_quiz_detail'),
]
