from django.contrib import admin
from .models import Department, Announcement, AcademicEvent

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'hod', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'target_audience', 'is_active', 'is_pinned', 'publish_date']
    list_filter = ['priority', 'target_audience', 'is_active', 'publish_date']
    search_fields = ['title', 'content']

@admin.register(AcademicEvent)
class AcademicEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'end_date', 'is_active']
    list_filter = ['event_type', 'is_active']
