"""
URL configuration for lms_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users.views import home_view
from users import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(('api_urls', 'api'), namespace='api')), # All API URLs under 'api' namespace
    path('auth/', include('users.urls_frontend')), # Frontend auth URLs
    path('courses/', include('courses.urls')), # Consolidated courses URLs
    path('enroll/', include('enrollments.urls')), # New Enrollment URLs
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'), # Direct URL for instructor dashboard
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'), # Direct URL for student dashboard
    path('', home_view, name='home'), # Homepage redirects based on auth/role
    path('lectures/', include('lectures.urls_frontend')), # Frontend lecture URLs
    path('quizzes/', include('quizzes.urls')), # New Quizzes URLs
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
