"""
Fee management views.
"""
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q

from .models import FeeVoucher, FeePayment
from .forms import FeeVoucherForm, FeePaymentForm, PaymentVerificationForm
from apps.accounts.decorators import admin_required


@login_required
def voucher_list(request):
    """List fee vouchers. Students see their own; admins see all."""
    if request.user.is_admin:
        vouchers = FeeVoucher.objects.select_related('student').all()
    else:
        vouchers = FeeVoucher.objects.filter(student=request.user)

    status_filter = request.GET.get('status', '')
    if status_filter:
        vouchers = vouchers.filter(status=status_filter)

    query = request.GET.get('q', '')
    if query:
        vouchers = vouchers.filter(
            Q(voucher_number__icontains=query) |
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query)
        )

    paginator = Paginator(vouchers, 15)
    page = request.GET.get('page')
    vouchers = paginator.get_page(page)

    return render(request, 'fees/voucher_list.html', {
        'vouchers': vouchers,
        'status_filter': status_filter,
        'query': query,
    })


@login_required
def voucher_detail(request, pk):
    """Voucher detail with payment history."""
    voucher = get_object_or_404(FeeVoucher.objects.select_related('student'), pk=pk)

    if not request.user.is_admin and voucher.student != request.user:
        messages.error(request, 'You do not have permission to view this voucher.')
        return redirect('fees:list')

    payments = voucher.payments.all()
    payment_form = FeePaymentForm()

    return render(request, 'fees/voucher_detail.html', {
        'voucher': voucher,
        'payments': payments,
        'payment_form': payment_form,
    })


@login_required
@admin_required
def voucher_create(request):
    """Admin: Create a fee voucher."""
    if request.method == 'POST':
        form = FeeVoucherForm(request.POST)
        if form.is_valid():
            voucher = form.save(commit=False)
            voucher.voucher_number = f"UAF-{timezone.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"
            voucher.created_by = request.user
            voucher.save()
            messages.success(request, f'Voucher {voucher.voucher_number} created successfully!')
            return redirect('fees:detail', pk=voucher.pk)
    else:
        form = FeeVoucherForm()

    from apps.accounts.models import User
    form.fields['student'].queryset = User.objects.filter(role__in=['ug_student', 'pg_student'], is_active=True)

    return render(request, 'fees/voucher_form.html', {'form': form})


@login_required
def upload_receipt(request, pk):
    """Student: Upload payment receipt for a voucher."""
    voucher = get_object_or_404(FeeVoucher, pk=pk, student=request.user)

    if request.method == 'POST':
        form = FeePaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.voucher = voucher
            payment.save()
            voucher.status = 'paid'
            voucher.save()
            messages.success(request, 'Payment receipt uploaded successfully!')
            return redirect('fees:detail', pk=voucher.pk)
    else:
        form = FeePaymentForm()

    return render(request, 'fees/upload_receipt.html', {'form': form, 'voucher': voucher})


@login_required
@admin_required
def verify_payment(request, pk):
    """Admin: Verify/reject a payment."""
    payment = get_object_or_404(FeePayment.objects.select_related('voucher'), pk=pk)

    if request.method == 'POST':
        form = PaymentVerificationForm(request.POST)
        if form.is_valid():
            payment.status = form.cleaned_data['status']
            payment.admin_remarks = form.cleaned_data['admin_remarks']
            payment.verified_by = request.user
            payment.verified_at = timezone.now()
            payment.save()

            # Update voucher status
            if payment.status == 'verified':
                payment.voucher.status = 'approved'
            elif payment.status == 'rejected':
                payment.voucher.status = 'rejected'
            payment.voucher.save()

            messages.success(request, f'Payment has been {payment.status}.')
            return redirect('fees:detail', pk=payment.voucher.pk)

    return redirect('fees:detail', pk=payment.voucher.pk)
