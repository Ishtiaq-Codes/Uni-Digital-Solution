"""
Course management forms.
"""
from django import forms
from .models import Course, CourseMaterial, Assignment

INPUT_CLASSES = 'w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-700 bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200'
SELECT_CLASSES = INPUT_CLASSES
TEXTAREA_CLASSES = INPUT_CLASSES + ' resize-none'
FILE_CLASSES = 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'code', 'description', 'department', 'semester', 'level', 'credit_hours', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Course title'}),
            'code': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g., CS-301'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 4}),
            'department': forms.Select(attrs={'class': SELECT_CLASSES}),
            'semester': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 1, 'max': 12}),
            'level': forms.Select(attrs={'class': SELECT_CLASSES}),
            'credit_hours': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 1, 'max': 6}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 border-slate-300 rounded'}),
        }


class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['title', 'description', 'material_type', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Material title'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 3}),
            'material_type': forms.Select(attrs={'class': SELECT_CLASSES}),
            'file': forms.FileInput(attrs={'class': FILE_CLASSES}),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'file', 'due_date', 'max_marks']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Assignment title'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 4}),
            'file': forms.FileInput(attrs={'class': FILE_CLASSES}),
            'due_date': forms.DateTimeInput(attrs={'class': INPUT_CLASSES, 'type': 'datetime-local'}),
            'max_marks': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 1}),
        }
