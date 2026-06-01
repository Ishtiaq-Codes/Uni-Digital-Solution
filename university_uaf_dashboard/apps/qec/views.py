"""
QEC views for feedback submission and analytics.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.core.paginator import Paginator

from .models import QECFeedback
from .forms import QECFeedbackForm
from apps.accounts.decorators import role_required


@login_required
def feedback_list(request):
    """View feedback based on role."""
    if request.user.is_admin or request.user.is_qec_officer:
        feedback = QECFeedback.objects.select_related('course').all()
    elif request.user.is_faculty:
        feedback = QECFeedback.objects.filter(
            course__instructor=request.user
        ).select_related('course')
    else:
        feedback = QECFeedback.objects.filter(
            student=request.user
        ).select_related('course')

    paginator = Paginator(feedback, 15)
    page = request.GET.get('page')
    feedback = paginator.get_page(page)

    return render(request, 'qec/feedback_list.html', {'feedback_list': feedback})


@login_required
@role_required('ug_student', 'pg_student')
def submit_feedback(request):
    """Student: Submit course feedback."""
    if request.method == 'POST':
        form = QECFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if not feedback.is_anonymous:
                feedback.student = request.user
            feedback.save()
            messages.success(request, 'Thank you! Your feedback has been submitted.')
            return redirect('qec:list')
    else:
        form = QECFeedbackForm()

    from apps.courses.models import CourseEnrollment
    enrolled_courses = CourseEnrollment.objects.filter(
        student=request.user
    ).values_list('course_id', flat=True)
    form.fields['course'].queryset = form.fields['course'].queryset.filter(id__in=enrolled_courses)

    return render(request, 'qec/submit_feedback.html', {'form': form})


@login_required
@role_required('super_admin', 'university_admin', 'qec_officer')
def analytics_dashboard(request):
    """QEC Analytics dashboard with charts."""
    from apps.courses.models import Course
    from apps.university.models import Department

    # Overall statistics
    total_feedback = QECFeedback.objects.count()
    avg_ratings = QECFeedback.objects.aggregate(
        avg_teaching=Avg('teaching_rating'),
        avg_content=Avg('content_rating'),
        avg_assessment=Avg('assessment_rating'),
        avg_overall=Avg('overall_rating'),
    )

    # Per-department stats
    dept_stats = QECFeedback.objects.values(
        'course__department__name'
    ).annotate(
        avg_rating=Avg('overall_rating'),
        count=Count('id')
    ).order_by('-avg_rating')

    # Per-course stats (top 10)
    course_stats = QECFeedback.objects.values(
        'course__title', 'course__code'
    ).annotate(
        avg_rating=Avg('overall_rating'),
        count=Count('id')
    ).order_by('-avg_rating')[:10]

    context = {
        'total_feedback': total_feedback,
        'avg_ratings': avg_ratings,
        'dept_stats': list(dept_stats),
        'course_stats': list(course_stats),
    }

    return render(request, 'qec/analytics.html', context)
