from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from courses.decorators import student_required # Assuming you have this decorator for students
from courses.models import Course # Import Course model
from .models import Enrollment
from progress.models import Progress
from .serializers import EnrollmentSerializer, ProgressSerializer

class IsEnrollmentOwner(permissions.BasePermission):
    """
    Custom permission to only allow students to view their own enrollments/progress.
    """
    def has_object_permission(self, request, view, obj):
        return obj.student == request.user

class EnrollmentListView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)

class ProgressDetailView(generics.RetrieveAPIView):
    serializer_class = ProgressSerializer
    permission_classes = [permissions.IsAuthenticated, IsEnrollmentOwner]

    def get_object(self):
        enrollment = get_object_or_404(Enrollment, student=self.request.user, course_id=self.kwargs['course_pk'])
        obj, created = Progress.objects.get_or_create(enrollment=enrollment)
        self.check_object_permissions(self.request, obj)
        return obj

@login_required
@student_required
def enroll_course_view(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.info(request, "You are already enrolled in this course.")
        return redirect('course-detail-public', pk=course.pk)

    Enrollment.objects.create(student=request.user, course=course)
    messages.success(request, f"Successfully enrolled in {course.title}!")
    return redirect('course-detail-public', pk=course.pk)
