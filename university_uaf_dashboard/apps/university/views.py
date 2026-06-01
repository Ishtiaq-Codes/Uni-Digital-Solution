"""
University views.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Department, Announcement, AcademicEvent


def departments_page(request):
    """Public/authenticated department listing."""
    departments = Department.objects.filter(is_active=True)
    return render(request, 'university/departments.html', {'departments': departments})


def department_detail(request, pk):
    """Department detail page."""
    department = get_object_or_404(Department, pk=pk)
    courses = department.courses.filter(is_active=True) if hasattr(department, 'courses') else []
    faculty = department.members.filter(user__role='faculty', user__is_active=True).select_related('user')

    return render(request, 'university/department_detail.html', {
        'department': department,
        'courses': courses,
        'faculty': faculty,
    })


def announcements_page(request):
    """Public announcements page."""
    announcements = Announcement.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now()
    )
    paginator = Paginator(announcements, 10)
    page = request.GET.get('page')
    announcements = paginator.get_page(page)

    return render(request, 'university/announcements.html', {'announcements': announcements})


def announcement_detail(request, pk):
    """Single announcement view."""
    announcement = get_object_or_404(Announcement, pk=pk, is_active=True)
    return render(request, 'university/announcement_detail.html', {'announcement': announcement})


@login_required
def academic_calendar(request):
    """Academic calendar with events."""
    events = AcademicEvent.objects.filter(is_active=True)
    event_type = request.GET.get('type', '')
    if event_type:
        events = events.filter(event_type=event_type)

    return render(request, 'university/calendar.html', {
        'events': events,
        'event_type_filter': event_type,
    })


def faculty_directory(request):
    """Public faculty directory."""
    from apps.accounts.models import User
    faculty = User.objects.filter(
        role='faculty', is_active=True
    ).select_related('profile').order_by('first_name')

    dept_filter = request.GET.get('department', '')
    if dept_filter:
        faculty = faculty.filter(profile__department_id=dept_filter)

    departments = Department.objects.filter(is_active=True)

    return render(request, 'university/faculty_directory.html', {
        'faculty': faculty,
        'departments': departments,
        'dept_filter': dept_filter,
    })


def about_page(request):
    """About the university."""
    return render(request, 'landing/about.html')


def features_page(request):
    """Features page."""
    return render(request, 'landing/features.html')


def contact_page(request):
    """Contact page."""
    return render(request, 'landing/contact.html')
