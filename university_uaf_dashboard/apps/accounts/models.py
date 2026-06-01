"""
User and Profile models for UAF Smart Dashboard.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager


class User(AbstractUser):
    """Custom User model with role-based access control."""

    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('university_admin', 'University Admin'),
        ('department_admin', 'Department Admin'),
        ('faculty', 'Faculty'),
        ('ug_student', 'Undergraduate Student'),
        ('pg_student', 'Postgraduate Student'),
        ('qec_officer', 'QEC Officer'),
    ]

    # Remove username field, use email as primary identifier
    username = None
    email = models.EmailField('Email Address', unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ug_student')
    registration_number = models.CharField(
        max_length=50, unique=True, blank=True, null=True,
        help_text='Student/Faculty registration number'
    )
    phone = models.CharField(max_length=20, blank=True)
    is_email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def is_admin(self):
        return self.role in ['super_admin', 'university_admin', 'department_admin']

    @property
    def is_student(self):
        return self.role in ['ug_student', 'pg_student']

    @property
    def is_ug_student(self):
        return self.role == 'ug_student'

    @property
    def is_pg_student(self):
        return self.role == 'pg_student'

    @property
    def is_faculty(self):
        return self.role == 'faculty'

    @property
    def is_qec_officer(self):
        return self.role == 'qec_officer'

    @property
    def role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)


class UserProfile(models.Model):
    """Extended profile information for users."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.ForeignKey(
        'university.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='members'
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)
    address = models.TextField(blank=True)
    semester = models.PositiveIntegerField(null=True, blank=True)
    session = models.CharField(max_length=20, blank=True, help_text='e.g., 2023-2027')
    designation = models.CharField(max_length=100, blank=True, help_text='For faculty members')
    specialization = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile: {self.user.get_full_name()}"

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None


class ActivityLog(models.Model):
    """Audit trail for user actions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities')
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"
