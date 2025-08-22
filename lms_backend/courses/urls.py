from django.urls import path
from . import views

urlpatterns = [
    # Frontend Views
    path('', views.CourseListView.as_view(), name='course-list-public'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course-detail-public'),
    path('instructor/new/', views.course_create_view, name='instructor_course_new'),
    path('instructor/<int:pk>/manage/', views.course_manage_view, name='instructor_course_manage'),
    path('instructor/<int:pk>/delete/', views.delete_course_view, name='delete_course'), # New URL for deleting courses
]
