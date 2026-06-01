"""
University data models - Departments, Announcements, Events.
"""
import uuid
from django.conf import settings
from django.db import models


class Department(models.Model):
    """University department."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    hod = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='headed_departments'
    )
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def student_count(self):
        return self.members.filter(
            user__role__in=['ug_student', 'pg_student'],
            user__is_active=True
        ).count()

    @property
    def faculty_count(self):
        return self.members.filter(
            user__role='faculty',
            user__is_active=True
        ).count()


class Announcement(models.Model):
    """University announcements and notices."""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    TARGET_CHOICES = [
        ('all', 'All Users'),
        ('students', 'All Students'),
        ('ug_students', 'UG Students Only'),
        ('pg_students', 'PG Students Only'),
        ('faculty', 'Faculty Only'),
        ('staff', 'Staff Only'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    target_audience = models.CharField(max_length=20, choices=TARGET_CHOICES, default='all')
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='announcements'
    )
    attachment = models.FileField(upload_to='announcements/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)
    publish_date = models.DateTimeField()
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_announcements'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-publish_date']

    def __str__(self):
        return self.title


class AcademicEvent(models.Model):
    """Academic calendar events."""
    EVENT_TYPES = [
        ('academic', 'Academic'),
        ('exam', 'Examination'),
        ('holiday', 'Holiday'),
        ('deadline', 'Deadline'),
        ('seminar', 'Seminar'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='academic')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.title} ({self.start_date})"
