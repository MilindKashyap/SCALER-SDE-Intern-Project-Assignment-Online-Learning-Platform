from rest_framework import serializers
from .models import Enrollment
from progress.models import Progress
from users.serializers import UserRegistrationSerializer # Re-using for student detail
from courses.serializers import CourseSerializer # Re-using for course detail

class EnrollmentSerializer(serializers.ModelSerializer):
    student_username = serializers.ReadOnlyField(source='student.username')
    course_title = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = Enrollment
        fields = ('id', 'student', 'student_username', 'course', 'course_title', 'created_at')
        read_only_fields = ('student', 'created_at')

class ProgressSerializer(serializers.ModelSerializer):
    enrollment_id = serializers.ReadOnlyField(source='enrollment.id')
    course_title = serializers.ReadOnlyField(source='enrollment.course.title')
    student_username = serializers.ReadOnlyField(source='enrollment.student.username')

    class Meta:
        model = Progress
        fields = ('enrollment_id', 'course_title', 'student_username', 'completed_lecture_ids', 'scores', 'last_seen_lecture_id')
