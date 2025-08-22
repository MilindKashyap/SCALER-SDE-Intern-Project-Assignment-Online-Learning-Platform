from django.db import models
from enrollments.models import Enrollment

class Progress(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='progress')
    completed_lecture_ids = models.JSONField(default=list) # JSON array of lecture IDs
    scores = models.JSONField(default=dict) # JSON object by lecture_id -> score
    last_seen_lecture_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Progress for {self.enrollment.student.username} in {self.enrollment.course.title}"
