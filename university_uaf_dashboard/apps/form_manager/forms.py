"""
Form manager forms.
"""
from django import forms
from .models import FormTemplate, FormSubmission

INPUT_CLASSES = 'w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-700 bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200'
FILE_CLASSES = 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'


class FormTemplateForm(forms.ModelForm):
    class Meta:
        model = FormTemplate
        fields = ['title', 'form_type', 'description', 'department', 'requires_supervisor', 'requires_hod', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'form_type': forms.Select(attrs={'class': INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASSES + ' resize-none', 'rows': 4}),
            'department': forms.Select(attrs={'class': INPUT_CLASSES}),
            'requires_supervisor': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 border-slate-300 rounded'}),
            'requires_hod': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 border-slate-300 rounded'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 border-slate-300 rounded'}),
        }


class FormSubmissionForm(forms.ModelForm):
    class Meta:
        model = FormSubmission
        fields = ['attachment']
        widgets = {
            'attachment': forms.FileInput(attrs={'class': FILE_CLASSES}),
        }


class FormReviewForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('approved', 'Approve'), ('rejected', 'Reject'), ('revision_requested', 'Request Revision')],
        widget=forms.Select(attrs={'class': INPUT_CLASSES})
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': INPUT_CLASSES + ' resize-none', 'rows': 3})
    )
