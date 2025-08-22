from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course-list-public'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course-detail-public'),
    path('instructor/courses/new/', views.course_create_view, name='instructor_course_new'),
    path('instructor/courses/<int:pk>/manage/', views.course_manage_view, name='instructor_course_manage'),
]
