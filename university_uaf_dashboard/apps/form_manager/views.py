"""
Form management views for UG and PG form submissions.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

from .models import FormTemplate, FormSubmission
from .forms import FormTemplateForm, FormSubmissionForm, FormReviewForm
from apps.accounts.decorators import admin_required


@login_required
def form_template_list(request):
    """List available form templates based on user role."""
    if request.user.is_admin:
        templates = FormTemplate.objects.filter(is_active=True)
    elif request.user.is_ug_student:
        templates = FormTemplate.objects.filter(is_active=True, form_type='ug')
    elif request.user.is_pg_student:
        templates = FormTemplate.objects.filter(is_active=True, form_type='pg')
    else:
        templates = FormTemplate.objects.filter(is_active=True)

    return render(request, 'forms/template_list.html', {'templates': templates})


@login_required
def form_submit(request, pk):
    """Submit a form from a template."""
    template = get_object_or_404(FormTemplate, pk=pk, is_active=True)

    # Access control
    if request.user.is_ug_student and template.form_type != 'ug':
        messages.error(request, 'This form is not available for undergraduate students.')
        return redirect('form_manager:list')
    if request.user.is_pg_student and template.form_type != 'pg':
        messages.error(request, 'This form is not available for postgraduate students.')
        return redirect('form_manager:list')

    if request.method == 'POST':
        form = FormSubmissionForm(request.POST, request.FILES)
        # Collect dynamic fields
        form_data = {}
        for key, value in request.POST.items():
            if key.startswith('field_'):
                form_data[key.replace('field_', '')] = value

        if form.is_valid():
            submission = form.save(commit=False)
            submission.template = template
            submission.student = request.user
            submission.form_data = form_data
            submission.save()
            messages.success(request, f'Form "{template.title}" submitted successfully!')
            return redirect('form_manager:submissions')
    else:
        form = FormSubmissionForm()

    return render(request, 'forms/form_submit.html', {
        'template': template,
        'form': form,
    })


@login_required
def my_submissions(request):
    """List user's form submissions."""
    submissions = FormSubmission.objects.filter(
        student=request.user
    ).select_related('template')

    status_filter = request.GET.get('status', '')
    if status_filter:
        submissions = submissions.filter(status=status_filter)

    paginator = Paginator(submissions, 15)
    page = request.GET.get('page')
    submissions = paginator.get_page(page)

    return render(request, 'forms/my_submissions.html', {
        'submissions': submissions,
        'status_filter': status_filter,
    })


@login_required
def submission_detail(request, pk):
    """View submission details."""
    submission = get_object_or_404(
        FormSubmission.objects.select_related('template', 'student', 'reviewed_by'),
        pk=pk
    )

    if not request.user.is_admin and submission.student != request.user:
        messages.error(request, 'You do not have permission to view this submission.')
        return redirect('form_manager:submissions')

    review_form = FormReviewForm() if request.user.is_admin else None

    return render(request, 'forms/submission_detail.html', {
        'submission': submission,
        'review_form': review_form,
    })


@login_required
@admin_required
def review_submission(request, pk):
    """Admin: Review a form submission."""
    submission = get_object_or_404(FormSubmission, pk=pk)

    if request.method == 'POST':
        form = FormReviewForm(request.POST)
        if form.is_valid():
            submission.status = form.cleaned_data['status']
            submission.remarks = form.cleaned_data['remarks']
            submission.reviewed_by = request.user
            submission.reviewed_at = timezone.now()
            submission.save()
            messages.success(request, f'Submission has been {submission.get_status_display().lower()}.')
            return redirect('form_manager:submission_detail', pk=pk)

    return redirect('form_manager:submission_detail', pk=pk)


@login_required
@admin_required
def all_submissions(request):
    """Admin: View all form submissions."""
    submissions = FormSubmission.objects.select_related('template', 'student').all()

    status_filter = request.GET.get('status', '')
    form_type_filter = request.GET.get('form_type', '')

    if status_filter:
        submissions = submissions.filter(status=status_filter)
    if form_type_filter:
        submissions = submissions.filter(template__form_type=form_type_filter)

    paginator = Paginator(submissions, 20)
    page = request.GET.get('page')
    submissions = paginator.get_page(page)

    return render(request, 'forms/all_submissions.html', {
        'submissions': submissions,
        'status_filter': status_filter,
        'form_type_filter': form_type_filter,
    })


@login_required
@admin_required
def create_template(request):
    """Admin: Create a form template."""
    if request.method == 'POST':
        form = FormTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            messages.success(request, f'Form template "{template.title}" created!')
            return redirect('form_manager:list')
    else:
        form = FormTemplateForm()

    return render(request, 'forms/template_form.html', {'form': form, 'action': 'Create'})
