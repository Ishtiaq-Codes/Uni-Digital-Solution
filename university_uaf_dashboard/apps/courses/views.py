"""
Course management views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse

from .models import Course, CourseMaterial, Assignment, CourseEnrollment
from .forms import CourseForm, CourseMaterialForm, AssignmentForm
from apps.accounts.decorators import faculty_required, role_required


@login_required
def course_list(request):
    """List courses with filtering."""
    courses = Course.objects.filter(is_active=True).select_related('department', 'instructor')
    query = request.GET.get('q', '')
    dept_filter = request.GET.get('department', '')
    semester_filter = request.GET.get('semester', '')
    level_filter = request.GET.get('level', '')

    if query:
        courses = courses.filter(Q(title__icontains=query) | Q(code__icontains=query))
    if dept_filter:
        courses = courses.filter(department_id=dept_filter)
    if semester_filter:
        courses = courses.filter(semester=semester_filter)
    if level_filter:
        courses = courses.filter(level=level_filter)

    from apps.university.models import Department
    departments = Department.objects.filter(is_active=True)

    paginator = Paginator(courses, 12)
    page = request.GET.get('page')
    courses = paginator.get_page(page)

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'departments': departments,
        'query': query,
        'dept_filter': dept_filter,
        'semester_filter': semester_filter,
        'level_filter': level_filter,
    })


@login_required
def course_detail(request, pk):
    """Course detail view with materials and assignments."""
    course = get_object_or_404(Course.objects.select_related('department', 'instructor'), pk=pk)
    materials = course.materials.all()
    assignments = course.assignments.all()
    is_enrolled = CourseEnrollment.objects.filter(student=request.user, course=course).exists()

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'materials': materials,
        'assignments': assignments,
        'is_enrolled': is_enrolled,
    })


@login_required
@faculty_required
def course_create(request):
    """Create a new course."""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, f'Course "{course.title}" created successfully!')
            return redirect('courses:detail', pk=course.pk)
    else:
        form = CourseForm()

    return render(request, 'courses/course_form.html', {'form': form, 'action': 'Create'})


@login_required
@faculty_required
def course_edit(request, pk):
    """Edit a course."""
    course = get_object_or_404(Course, pk=pk)
    if course.instructor != request.user and not request.user.is_admin:
        messages.error(request, 'You can only edit your own courses.')
        return redirect('courses:detail', pk=pk)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.title}" updated successfully!')
            return redirect('courses:detail', pk=course.pk)
    else:
        form = CourseForm(instance=course)

    return render(request, 'courses/course_form.html', {'form': form, 'action': 'Edit', 'course': course})


@login_required
@faculty_required
def upload_material(request, pk):
    """Upload course material."""
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.uploaded_by = request.user
            material.save()
            messages.success(request, f'Material "{material.title}" uploaded successfully!')
            return redirect('courses:detail', pk=course.pk)
    else:
        form = CourseMaterialForm()

    return render(request, 'courses/upload_material.html', {'form': form, 'course': course})


@login_required
@faculty_required
def create_assignment(request, pk):
    """Create a new assignment."""
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, f'Assignment "{assignment.title}" created successfully!')
            return redirect('courses:detail', pk=course.pk)
    else:
        form = AssignmentForm()

    return render(request, 'courses/assignment_form.html', {'form': form, 'course': course})


@login_required
def download_material(request, pk):
    """Download a course material and increment counter."""
    material = get_object_or_404(CourseMaterial, pk=pk)
    material.download_count += 1
    material.save(update_fields=['download_count'])
    return FileResponse(material.file.open('rb'), as_attachment=True, filename=material.file.name.split('/')[-1])


@login_required
def enroll_course(request, pk):
    """Enroll in a course."""
    if request.method == 'POST':
        course = get_object_or_404(Course, pk=pk)
        enrollment, created = CourseEnrollment.objects.get_or_create(
            student=request.user, course=course,
            defaults={'semester': course.semester}
        )
        if created:
            messages.success(request, f'You have been enrolled in {course.title}!')
        else:
            messages.info(request, 'You are already enrolled in this course.')
    return redirect('courses:detail', pk=pk)
