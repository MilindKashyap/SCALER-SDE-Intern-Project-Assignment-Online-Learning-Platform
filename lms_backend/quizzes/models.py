from django.db import models
from lectures.models import QuizLecture
from users.models import User

# Create your models here.

class Question(models.Model):
    quiz = models.ForeignKey(QuizLecture, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    options = models.JSONField() # JSON array of strings
    correct_index = models.PositiveIntegerField() # Index of the correct option in the options array

    def __str__(self):
        return f"Question: {self.text[:50]}... (Quiz: {self.quiz.lecture.title})"

class QuizSubmission(models.Model):
    quiz_lecture = models.ForeignKey(QuizLecture, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.student.username} for {self.quiz_lecture.lecture.title}"

class Answer(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option_index = models.PositiveIntegerField()

    def __str__(self):
        return f"Answer for {self.question.text[:50]}... in {self.submission}"

class Grade(models.Model):
    submission = models.OneToOneField(QuizSubmission, on_delete=models.CASCADE, related_name='grade')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_grades')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Grade for {self.submission} - Score: {self.score}"
