from django.urls import path
from . import views
from .views import EnrollmentListView, ProgressDetailView

urlpatterns = [
    path('enrollments/', EnrollmentListView.as_view(), name='enrollment-list'),
    path('enrollments/<int:course_pk>/progress/', ProgressDetailView.as_view(), name='progress-detail'),
    path('course/<int:course_pk>/enroll/', views.enroll_course_view, name='enroll_course'), # New URL for enrolling in courses
]
