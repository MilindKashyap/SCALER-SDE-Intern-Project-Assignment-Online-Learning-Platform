from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    instructor_username = serializers.ReadOnlyField(source='instructor.username')

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'instructor', 'instructor_username', 'created_at', 'is_published')
        read_only_fields = ('instructor', 'created_at')
