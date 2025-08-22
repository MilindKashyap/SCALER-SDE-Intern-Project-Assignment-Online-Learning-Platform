from django.db import models
from django.utils import timezone
from courses.models import Course

class Lecture(models.Model):
    LECTURE_TYPES = (
        ('QUIZ', 'Quiz'),
        ('VIDEO', 'Video'),
        ('PDF', 'PDF'),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=LECTURE_TYPES)
    order_index = models.PositiveIntegerField()

    class Meta:
        ordering = ['order_index']
        unique_together = ('course', 'order_index')

    def __str__(self):
        return f"{self.title} ({self.type}) - Course: {self.course.title}"

class ReadingLecture(models.Model):
    lecture = models.OneToOneField(Lecture, on_delete=models.CASCADE, primary_key=True, related_name='reading_lecture')
    content_url = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to='lecture_files/', blank=True, null=True)

    def __str__(self):
        return f"Reading: {self.lecture.title}"

class QuizLecture(models.Model):
    lecture = models.OneToOneField(Lecture, on_delete=models.CASCADE, primary_key=True, related_name='quiz_lecture')
    start_date = models.DateTimeField(default=timezone.now, help_text="When the quiz becomes available")
    end_date = models.DateTimeField(default=timezone.now, help_text="When the quiz closes")
    duration = models.PositiveIntegerField(default=30, help_text="Duration in minutes")

    def __str__(self):
        return f"Quiz: {self.lecture.title}"

    def is_active(self):
        """Check if the quiz is currently active (within time window)"""
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def is_expired(self):
        """Check if the quiz has expired"""
        return timezone.now() > self.end_date

    def is_not_started(self):
        """Check if the quiz hasn't started yet"""
        return timezone.now() < self.start_date
