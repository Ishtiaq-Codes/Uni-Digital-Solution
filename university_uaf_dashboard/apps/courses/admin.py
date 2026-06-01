from django.contrib import admin
from .models import Course, CourseMaterial, Assignment, CourseEnrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'department', 'instructor', 'semester', 'level', 'is_active']
    list_filter = ['department', 'level', 'semester', 'is_active']
    search_fields = ['title', 'code']

@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'material_type', 'uploaded_by', 'download_count', 'created_at']
    list_filter = ['material_type', 'created_at']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'due_date', 'max_marks', 'created_at']
    list_filter = ['due_date', 'course']

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'semester', 'enrolled_at']
    list_filter = ['semester', 'enrolled_at']
