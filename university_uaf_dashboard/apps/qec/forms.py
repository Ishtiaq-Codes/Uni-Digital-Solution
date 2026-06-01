"""
QEC forms.
"""
from django import forms
from .models import QECFeedback

INPUT_CLASSES = 'w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-700 bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200'

RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]


class QECFeedbackForm(forms.ModelForm):
    teaching_rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'text-indigo-600'}),
        label='Teaching Quality'
    )
    content_rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'text-indigo-600'}),
        label='Course Content'
    )
    assessment_rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'text-indigo-600'}),
        label='Assessment Quality'
    )
    overall_rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'text-indigo-600'}),
        label='Overall Satisfaction'
    )

    class Meta:
        model = QECFeedback
        fields = ['course', 'teaching_rating', 'content_rating', 'assessment_rating', 'overall_rating', 'comments', 'is_anonymous']
        widgets = {
            'course': forms.Select(attrs={'class': INPUT_CLASSES}),
            'comments': forms.Textarea(attrs={'class': INPUT_CLASSES + ' resize-none', 'rows': 4, 'placeholder': 'Share your feedback...'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 border-slate-300 rounded'}),
        }
