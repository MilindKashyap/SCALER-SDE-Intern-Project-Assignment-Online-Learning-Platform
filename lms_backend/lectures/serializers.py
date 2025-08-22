from rest_framework import serializers
from .models import Lecture, ReadingLecture, QuizLecture
from quizzes.models import Question

class ReadingLectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingLecture
        fields = ('content_text', 'content_url', 'file')

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'text', 'options', 'correct_index')

class QuizLectureSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = QuizLecture
        fields = ('questions',)

class LectureSerializer(serializers.ModelSerializer):
    reading_lecture = ReadingLectureSerializer(read_only=True)
    quiz_lecture = QuizLectureSerializer(read_only=True)

    class Meta:
        model = Lecture
        fields = ('id', 'course', 'title', 'type', 'order_index', 'reading_lecture', 'quiz_lecture')
        read_only_fields = ('course',)
