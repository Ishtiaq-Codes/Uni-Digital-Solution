"""
Fee Voucher Management models.
"""
import uuid
from django.conf import settings
from django.db import models


class FeeVoucher(models.Model):
    """Fee voucher for students."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    SEMESTER_CHOICES = [(f'Semester {i}', f'Semester {i}') for i in range(1, 13)]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fee_vouchers'
    )
    voucher_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES)
    academic_year = models.CharField(max_length=20, help_text='e.g., 2024-2025')
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_vouchers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Fee Voucher'
        verbose_name_plural = 'Fee Vouchers'

    def __str__(self):
        return f"Voucher {self.voucher_number} - {self.student}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status == 'pending'


class FeePayment(models.Model):
    """Payment record for fee vouchers."""
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voucher = models.ForeignKey(FeeVoucher, on_delete=models.CASCADE, related_name='payments')
    receipt = models.FileField(upload_to='vouchers/receipts/')
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    admin_remarks = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='verified_payments'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Payment for {self.voucher.voucher_number}"
