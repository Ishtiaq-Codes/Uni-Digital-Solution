from django.contrib import admin
from .models import FormTemplate, FormSubmission

@admin.register(FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'form_type', 'department', 'is_active', 'requires_supervisor', 'created_at']
    list_filter = ['form_type', 'is_active']
    search_fields = ['title']

@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'template', 'status', 'submitted_at', 'reviewed_at']
    list_filter = ['status', 'template__form_type', 'submitted_at']
    search_fields = ['student__email', 'template__title']
