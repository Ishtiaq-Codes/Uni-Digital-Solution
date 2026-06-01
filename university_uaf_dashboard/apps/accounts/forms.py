"""
Forms for authentication and user profile management.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from .models import UserProfile

User = get_user_model()

# Tailwind CSS classes for form fields
INPUT_CLASSES = 'w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-700 bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200 placeholder-slate-400'
SELECT_CLASSES = 'w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-700 bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200'
TEXTAREA_CLASSES = 'w-full px-4 py-2.5 border border-slate-300 rounded-lg text-slate-700 bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200 placeholder-slate-400 resize-none'
CHECKBOX_CLASSES = 'h-4 w-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500'


class LoginForm(forms.Form):
    """Login form supporting email or registration number."""
    username = forms.CharField(
        label='Email or Registration Number',
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Enter email or registration number',
            'autofocus': True,
            'id': 'login-username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Enter your password',
            'id': 'login-password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': CHECKBOX_CLASSES,
            'id': 'login-remember',
        })
    )


class RegistrationForm(forms.ModelForm):
    """User registration form."""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Create a password',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Confirm your password',
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'registration_number', 'phone', 'role']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Email address'}),
            'registration_number': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g., 2021-ag-1234'}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Phone number'}),
            'role': forms.Select(attrs={'class': SELECT_CLASSES}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """User profile edit form."""
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES})
    )

    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'address', 'semester', 'session', 'designation', 'specialization']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
            'bio': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 3, 'placeholder': 'Tell us about yourself...'}),
            'address': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 2, 'placeholder': 'Your address'}),
            'semester': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 1, 'max': 12}),
            'session': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g., 2023-2027'}),
            'designation': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g., Assistant Professor'}),
            'specialization': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g., Machine Learning'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Styled password change form."""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Current password',
        })
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'New password',
        })
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Confirm new password',
        })
    )


class ForgotPasswordForm(forms.Form):
    """Forgot password form."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Enter your registered email',
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Styled password reset form."""
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Enter new password',
        })
    )
    new_password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Confirm new password',
        })
    )


class AdminUserCreationForm(forms.ModelForm):
    """
    Admin-only form for creating new users.
    Enforces role-based restrictions:
    - Super Admin can create any role
    - University Admin cannot create Super Admin
    """
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Set a password for this user',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Confirm the password',
        })
    )
    department = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': SELECT_CLASSES}),
        help_text='Required for students and department-specific roles',
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'registration_number', 'phone', 'role']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Email address'}),
            'registration_number': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g., 2021-ag-1234'}),
            'phone': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Phone number'}),
            'role': forms.Select(attrs={'class': SELECT_CLASSES}),
        }

    def __init__(self, *args, creator=None, **kwargs):
        """
        Accept creator (the admin creating this user) to enforce role restrictions.
        """
        super().__init__(*args, **kwargs)

        # Import here to avoid circular imports
        from apps.university.models import Department
        self.fields['department'].queryset = Department.objects.all()

        self.creator = creator

        # Restrict role choices based on creator's role
        if creator:
            if creator.role == 'university_admin':
                # University Admin cannot create Super Admin
                self.fields['role'].choices = [
                    (key, label) for key, label in User.ROLE_CHOICES
                    if key != 'super_admin'
                ]
            elif creator.role == 'super_admin' or creator.is_superuser:
                # Super Admin can create any role
                self.fields['role'].choices = User.ROLE_CHOICES
            else:
                # Should never happen due to decorators, but safety net
                self.fields['role'].choices = []

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def clean_role(self):
        """SERVER-SIDE role validation — prevents privilege escalation attacks."""
        role = self.cleaned_data.get('role')

        if self.creator:
            # University Admin cannot create Super Admin (even via manual POST)
            if self.creator.role == 'university_admin' and role == 'super_admin':
                raise forms.ValidationError(
                    'You do not have permission to create a Super Admin account.'
                )
            # Only Super Admin or University Admin should use this form at all
            if self.creator.role not in ('super_admin', 'university_admin') and not self.creator.is_superuser:
                raise forms.ValidationError(
                    'You do not have permission to create users.'
                )
        return role

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            # Assign department to user profile
            department = self.cleaned_data.get('department')
            if department and hasattr(user, 'profile'):
                user.profile.department = department
                user.profile.save()
        return user


class AdminPasswordResetForm(forms.Form):
    """Form for admin to reset a user's password."""
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Enter new password',
        })
    )
    new_password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Confirm new password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

