"""
Course Management models.
"""
import uuid
from django.conf import settings
from django.db import models


class Course(models.Model):
    """Course model."""
    LEVEL_CHOICES = [
        ('ug', 'Undergraduate'),
        ('pg', 'Postgraduate'),
        ('both', 'Both'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        'university.Department', on_delete=models.CASCADE, related_name='courses'
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='teaching_courses'
    )
    semester = models.PositiveIntegerField(default=1)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='ug')
    credit_hours = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return f"{self.code} - {self.title}"


class CourseMaterial(models.Model):
    """Course materials (lectures, notes, etc.)."""
    MATERIAL_TYPES = [
        ('lecture', 'Lecture Notes'),
        ('syllabus', 'Syllabus'),
        ('assignment', 'Assignment'),
        ('ppt', 'Presentation'),
        ('video', 'Video'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='lecture')
    file = models.FileField(upload_to='course_materials/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.code} - {self.title}"


class Assignment(models.Model):
    """Course assignments."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='course_materials/assignments/', blank=True, null=True)
    due_date = models.DateTimeField()
    max_marks = models.PositiveIntegerField(default=100)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.course.code} - {self.title}"

    @property
    def is_overdue(self):
        from django.utils import timezone
        return timezone.now() > self.due_date


class CourseEnrollment(models.Model):
    """Student course enrollments."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    semester = models.PositiveIntegerField(default=1)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student} - {self.course}"
