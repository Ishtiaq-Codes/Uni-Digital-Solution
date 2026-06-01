from django.contrib import admin
from .models import FeeVoucher, FeePayment

@admin.register(FeeVoucher)
class FeeVoucherAdmin(admin.ModelAdmin):
    list_display = ['voucher_number', 'student', 'amount', 'semester', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'semester', 'due_date']
    search_fields = ['voucher_number', 'student__email', 'student__first_name']

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['voucher', 'status', 'transaction_id', 'submitted_at', 'verified_at']
    list_filter = ['status', 'submitted_at']
