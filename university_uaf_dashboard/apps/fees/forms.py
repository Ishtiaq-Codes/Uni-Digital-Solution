"""
Fee management forms.
"""
from django import forms
from .models import FeeVoucher, FeePayment

INPUT_CLASSES = 'w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-700 bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200'
FILE_CLASSES = 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'


class FeeVoucherForm(forms.ModelForm):
    class Meta:
        model = FeeVoucher
        fields = ['student', 'amount', 'semester', 'academic_year', 'due_date', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': INPUT_CLASSES}),
            'amount': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 0, 'step': '0.01'}),
            'semester': forms.Select(attrs={'class': INPUT_CLASSES}),
            'academic_year': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': '2024-2025'}),
            'due_date': forms.DateInput(attrs={'class': INPUT_CLASSES, 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': INPUT_CLASSES + ' resize-none', 'rows': 3}),
        }


class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ['receipt', 'transaction_id']
        widgets = {
            'receipt': forms.FileInput(attrs={'class': FILE_CLASSES, 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'transaction_id': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Bank transaction ID'}),
        }


class PaymentVerificationForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('verified', 'Approve'), ('rejected', 'Reject')],
        widget=forms.Select(attrs={'class': INPUT_CLASSES})
    )
    admin_remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': INPUT_CLASSES + ' resize-none', 'rows': 3, 'placeholder': 'Admin remarks...'})
    )
