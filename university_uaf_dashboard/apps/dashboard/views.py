"""
Dashboard views - Landing page and role-based dashboard routing.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.utils import timezone


def landing_page(request):
    """Public landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    from apps.university.models import Department, Announcement
    from apps.accounts.models import User

    departments = Department.objects.filter(is_active=True)[:6]
    announcements = Announcement.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now()
    ).order_by('-publish_date')[:4]

    stats = {
        'students': User.objects.filter(role__in=['ug_student', 'pg_student'], is_active=True).count(),
        'faculty': User.objects.filter(role='faculty', is_active=True).count(),
        'departments': Department.objects.filter(is_active=True).count(),
        'courses': 0,
    }

    try:
        from apps.courses.models import Course
        stats['courses'] = Course.objects.filter(is_active=True).count()
    except Exception:
        pass

    return render(request, 'landing/home.html', {
        'departments': departments,
        'announcements': announcements,
        'stats': stats,
    })


@login_required
def dashboard_home(request):
    """Role-based dashboard routing."""
    user = request.user

    if user.role in ['super_admin', 'university_admin', 'department_admin']:
        return admin_dashboard(request)
    elif user.role == 'faculty':
        return faculty_dashboard(request)
    elif user.role in ['ug_student', 'pg_student']:
        return student_dashboard(request)
    elif user.role == 'qec_officer':
        return qec_dashboard(request)
    else:
        return student_dashboard(request)


def admin_dashboard(request):
    """Admin dashboard with overview statistics."""
    from apps.accounts.models import User
    from apps.university.models import Department, Announcement

    context = {
        'total_students': User.objects.filter(role__in=['ug_student', 'pg_student'], is_active=True).count(),
        'total_faculty': User.objects.filter(role='faculty', is_active=True).count(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'recent_announcements': Announcement.objects.filter(is_active=True).order_by('-publish_date')[:5],
        'recent_users': User.objects.order_by('-date_joined')[:5],
    }

    try:
        from apps.courses.models import Course
        context['total_courses'] = Course.objects.filter(is_active=True).count()
    except Exception:
        context['total_courses'] = 0

    try:
        from apps.fees.models import FeeVoucher
        context['pending_vouchers'] = FeeVoucher.objects.filter(status='pending').count()
    except Exception:
        context['pending_vouchers'] = 0

    try:
        from apps.form_manager.models import FormSubmission
        context['pending_forms'] = FormSubmission.objects.filter(status='pending').count()
    except Exception:
        context['pending_forms'] = 0

    return render(request, 'dashboard/admin_dashboard.html', context)


def faculty_dashboard(request):
    """Faculty dashboard."""
    context = {
        'my_courses': [],
        'pending_assignments': 0,
    }

    try:
        from apps.courses.models import Course
        context['my_courses'] = Course.objects.filter(instructor=request.user, is_active=True)
        context['total_courses'] = context['my_courses'].count()
    except Exception:
        context['total_courses'] = 0

    return render(request, 'dashboard/faculty_dashboard.html', context)


def student_dashboard(request):
    """Student dashboard."""
    context = {
        'enrolled_courses': [],
        'fee_status': 'N/A',
        'pending_forms': 0,
    }

    try:
        from apps.courses.models import CourseEnrollment
        enrollments = CourseEnrollment.objects.filter(
            student=request.user
        ).select_related('course')
        context['enrolled_courses'] = enrollments
        context['total_enrolled'] = enrollments.count()
    except Exception:
        context['total_enrolled'] = 0

    try:
        from apps.fees.models import FeeVoucher
        latest_voucher = FeeVoucher.objects.filter(student=request.user).order_by('-created_at').first()
        if latest_voucher:
            context['fee_status'] = latest_voucher.get_status_display()
            context['latest_voucher'] = latest_voucher
    except Exception:
        pass

    try:
        from apps.form_manager.models import FormSubmission
        context['pending_forms'] = FormSubmission.objects.filter(
            student=request.user, status='pending'
        ).count()
    except Exception:
        pass

    return render(request, 'dashboard/student_dashboard.html', context)


def qec_dashboard(request):
    """QEC Officer dashboard."""
    context = {
        'total_feedback': 0,
        'avg_rating': 0,
    }

    try:
        from apps.qec.models import QECFeedback
        from django.db.models import Avg
        feedback = QECFeedback.objects.all()
        context['total_feedback'] = feedback.count()
        context['avg_rating'] = feedback.aggregate(avg=Avg('overall_rating'))['avg'] or 0
    except Exception:
        pass

    return render(request, 'dashboard/qec_dashboard.html', context)


@login_required
def global_search(request):
    """Global search across all modules."""
    query = request.GET.get('q', '').strip()
    results = {
        'users': [],
        'courses': [],
        'announcements': [],
        'departments': [],
    }

    if query and len(query) >= 2:
        from apps.accounts.models import User
        results['users'] = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(registration_number__icontains=query)
        )[:10]

        try:
            from apps.courses.models import Course
            results['courses'] = Course.objects.filter(
                Q(title__icontains=query) |
                Q(code__icontains=query)
            )[:10]
        except Exception:
            pass

        try:
            from apps.university.models import Announcement, Department
            results['announcements'] = Announcement.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            )[:10]
            results['departments'] = Department.objects.filter(
                Q(name__icontains=query) |
                Q(code__icontains=query)
            )[:10]
        except Exception:
            pass

    total_results = sum(len(v) for v in results.values())

    return render(request, 'dashboard/search_results.html', {
        'query': query,
        'results': results,
        'total_results': total_results,
    })
