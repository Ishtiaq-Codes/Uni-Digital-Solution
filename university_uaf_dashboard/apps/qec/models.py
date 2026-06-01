"""
QEC (Quality Enhancement Cell) models.
"""
import uuid
from django.conf import settings
from django.db import models


class QECFeedback(models.Model):
    """Student feedback for courses and faculty."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE, related_name='qec_feedback'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='qec_feedback'
    )
    # Ratings (1-5)
    teaching_rating = models.PositiveIntegerField(default=3, help_text='1-5 rating')
    content_rating = models.PositiveIntegerField(default=3)
    assessment_rating = models.PositiveIntegerField(default=3)
    overall_rating = models.PositiveIntegerField(default=3)
    comments = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=True)
    semester = models.CharField(max_length=20, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'QEC Feedback'
        verbose_name_plural = 'QEC Feedback'

    def __str__(self):
        name = 'Anonymous' if self.is_anonymous else str(self.student)
        return f"Feedback for {self.course} by {name}"

    @property
    def average_rating(self):
        return round(
            (self.teaching_rating + self.content_rating +
             self.assessment_rating + self.overall_rating) / 4, 1
        )
