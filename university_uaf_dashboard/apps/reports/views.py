"""
Reports & Analytics views.
"""
import csv
import io
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone

from apps.accounts.decorators import admin_required


@login_required
@admin_required
def analytics_dashboard(request):
    """Main analytics dashboard with charts."""
    from apps.accounts.models import User
    from apps.university.models import Department
    from apps.courses.models import Course
    from apps.fees.models import FeeVoucher
    from apps.form_manager.models import FormSubmission
    from apps.qec.models import QECFeedback

    # User stats
    students_by_dept = list(User.objects.filter(
        role__in=['ug_student', 'pg_student'],
        is_active=True,
        profile__department__isnull=False
    ).values('profile__department__name').annotate(
        count=Count('id')
    ).order_by('-count'))

    # Fee stats
    fee_stats = FeeVoucher.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        approved=Count('id', filter=Q(status='approved')),
        rejected=Count('id', filter=Q(status='rejected')),
        total_amount=Sum('amount'),
    )

    # Form stats
    form_stats = FormSubmission.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        approved=Count('id', filter=Q(status='approved')),
        rejected=Count('id', filter=Q(status='rejected')),
    )

    # QEC stats
    qec_avg = QECFeedback.objects.aggregate(
        avg_overall=Avg('overall_rating'),
        avg_teaching=Avg('teaching_rating'),
        total=Count('id'),
    )

    # Monthly registrations (last 6 months)
    from datetime import timedelta
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_users = list(User.objects.filter(
        date_joined__gte=six_months_ago
    ).extra(
        select={'month': "strftime('%%Y-%%m', date_joined)"}
    ).values('month').annotate(count=Count('id')).order_by('month'))

    context = {
        'students_by_dept': students_by_dept,
        'fee_stats': fee_stats,
        'form_stats': form_stats,
        'qec_avg': qec_avg,
        'monthly_users': monthly_users,
        'total_users': User.objects.filter(is_active=True).count(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'total_courses': Course.objects.filter(is_active=True).count(),
    }

    return render(request, 'reports/analytics.html', context)


@login_required
@admin_required
def export_students_csv(request):
    """Export student list as CSV."""
    from apps.accounts.models import User

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Registration Number', 'Role', 'Department', 'Semester', 'Status', 'Date Joined'])

    students = User.objects.filter(
        role__in=['ug_student', 'pg_student']
    ).select_related('profile', 'profile__department')

    for student in students:
        dept_name = student.profile.department.name if student.profile.department else 'N/A'
        writer.writerow([
            student.get_full_name(),
            student.email,
            student.registration_number or 'N/A',
            student.get_role_display() if hasattr(student, 'get_role_display') else student.role,
            dept_name,
            student.profile.semester or 'N/A',
            'Active' if student.is_active else 'Inactive',
            student.date_joined.strftime('%Y-%m-%d'),
        ])

    return response


@login_required
@admin_required
def export_fees_csv(request):
    """Export fee vouchers as CSV."""
    from apps.fees.models import FeeVoucher

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fee_vouchers_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Voucher No', 'Student', 'Email', 'Amount', 'Semester', 'Status', 'Due Date', 'Created'])

    vouchers = FeeVoucher.objects.select_related('student').all()

    for v in vouchers:
        writer.writerow([
            v.voucher_number,
            v.student.get_full_name(),
            v.student.email,
            v.amount,
            v.semester,
            v.status,
            v.due_date.strftime('%Y-%m-%d'),
            v.created_at.strftime('%Y-%m-%d'),
        ])

    return response


@login_required
@admin_required
def export_qec_csv(request):
    """Export QEC feedback as CSV."""
    from apps.qec.models import QECFeedback

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="qec_feedback_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Course', 'Student', 'Teaching', 'Content', 'Assessment', 'Overall', 'Comments', 'Date'])

    feedback = QECFeedback.objects.select_related('course', 'student').all()

    for f in feedback:
        student_name = 'Anonymous' if f.is_anonymous else (str(f.student) if f.student else 'N/A')
        writer.writerow([
            str(f.course),
            student_name,
            f.teaching_rating,
            f.content_rating,
            f.assessment_rating,
            f.overall_rating,
            f.comments[:200],
            f.submitted_at.strftime('%Y-%m-%d'),
        ])

    return response
