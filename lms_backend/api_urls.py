from django.urls import path, include

urlpatterns = [
    path('auth/', include('users.urls')),
    path('courses/', include('courses.api_urls')), # API endpoints for courses
    path('lectures/', include('lectures.api_urls')), # API endpoints for lectures
    path('enrollments/', include('enrollments.urls')),
]
