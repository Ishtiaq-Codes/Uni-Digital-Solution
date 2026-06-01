"""
Notification system models.
"""
import uuid
from django.conf import settings
from django.db import models


class Notification(models.Model):
    """In-app notification."""
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('announcement', 'Announcement'),
        ('fee', 'Fee Update'),
        ('form', 'Form Update'),
        ('course', 'Course Update'),
        ('qec', 'QEC Alert'),
        ('assignment', 'Assignment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True, help_text='URL to navigate to')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.title} → {self.recipient}"

    @classmethod
    def create_notification(cls, recipient, title, message, notification_type='info', link=''):
        """Helper to create a notification."""
        return cls.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link
        )

    @classmethod
    def notify_all(cls, recipients, title, message, notification_type='info', link=''):
        """Send notification to multiple users."""
        notifications = [
            cls(recipient=user, title=title, message=message,
                notification_type=notification_type, link=link)
            for user in recipients
        ]
        cls.objects.bulk_create(notifications)
