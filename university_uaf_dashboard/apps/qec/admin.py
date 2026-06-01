from django.contrib import admin
from .models import QECFeedback

@admin.register(QECFeedback)
class QECFeedbackAdmin(admin.ModelAdmin):
    list_display = ['course', 'student', 'overall_rating', 'is_anonymous', 'submitted_at']
    list_filter = ['overall_rating', 'is_anonymous', 'submitted_at']
    search_fields = ['course__title', 'comments']
