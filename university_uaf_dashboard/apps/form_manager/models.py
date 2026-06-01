"""
Form Manager models - UG Forms and PG GS-10 forms.
"""
import uuid
from django.conf import settings
from django.db import models


class FormTemplate(models.Model):
    """Reusable form templates for UG/PG submissions."""
    FORM_TYPE_CHOICES = [
        ('ug', 'Undergraduate'),
        ('pg', 'Postgraduate (GS-10)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    form_type = models.CharField(max_length=5, choices=FORM_TYPE_CHOICES)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        'university.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='form_templates'
    )
    fields_schema = models.JSONField(
        default=list, blank=True,
        help_text='JSON schema defining form fields'
    )
    is_active = models.BooleanField(default=True)
    requires_supervisor = models.BooleanField(default=False, help_text='PG forms requiring supervisor approval')
    requires_hod = models.BooleanField(default=False, help_text='Forms requiring HOD approval')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Form Template'

    def __str__(self):
        return f"{self.get_form_type_display()} - {self.title}"


class FormSubmission(models.Model):
    """Student form submissions."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('revision_requested', 'Revision Requested'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='form_submissions'
    )
    form_data = models.JSONField(default=dict, blank=True)
    attachment = models.FileField(upload_to='forms/submissions/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_submissions'
    )
    supervisor_approved = models.BooleanField(null=True, blank=True)
    hod_approved = models.BooleanField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Form Submission'

    def __str__(self):
        return f"{self.student} - {self.template.title}"

    @property
    def form_type(self):
        return self.template.form_type
