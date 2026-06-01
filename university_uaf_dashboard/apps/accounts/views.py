"""
Views for authentication, profile management, and user administration.
User creation is also available via admin dashboards for authorized roles.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponseForbidden

from .forms import (
    LoginForm, ProfileForm,
    CustomPasswordChangeForm, ForgotPasswordForm, CustomSetPasswordForm,
    AdminUserCreationForm, AdminPasswordResetForm,
)
from .decorators import admin_required, senior_admin_required
from .models import UserProfile, ActivityLog

User = get_user_model()


# =====================================================
# PUBLIC AUTH VIEWS (login, logout, register, forgot/reset password)
# =====================================================

@never_cache
@ensure_csrf_cookie
def login_view(request):
    """Handle user login with email or registration number."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                # Set session expiry
                if not remember_me:
                    request.session.set_expiry(0)  # Browser close
                else:
                    request.session.set_expiry(86400 * 30)  # 30 days

                # Log activity
                ActivityLog.objects.create(
                    user=user,
                    action='login',
                    details=f'User logged in from {get_client_ip(request)}',
                    ip_address=get_client_ip(request)
                )

                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                next_url = request.GET.get('next', 'dashboard:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email/registration number or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@never_cache
def logout_view(request):
    """Handle user logout."""
    if request.user.is_authenticated:
        ActivityLog.objects.create(
            user=request.user,
            action='logout',
            details='User logged out',
            ip_address=get_client_ip(request)
        )
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@never_cache
def register_view(request):
    """
    PUBLIC REGISTRATION IS DISABLED.
    All requests (GET and POST) are blocked and redirected to login.
    User creation is restricted to admin dashboards only.
    """
    messages.warning(request, 'Public registration is disabled. Please contact your administrator for an account.')
    return redirect('accounts:login')


@never_cache
@ensure_csrf_cookie
def forgot_password_view(request):
    """Handle forgot password - send reset email."""
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # In development, print to console
                reset_url = f"{request.scheme}://{request.get_host()}/accounts/reset-password/{uid}/{token}/"
                print(f"\n[PASSWORD RESET LINK]: {reset_url}\n")

                try:
                    send_mail(
                        'Password Reset - UAF Dashboard',
                        f'Click the link to reset your password: {reset_url}',
                        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@uaf.edu.pk',
                        [email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

                messages.success(request, 'If an account exists with that email, a reset link has been sent.')
            except User.DoesNotExist:
                # Don't reveal whether email exists
                messages.success(request, 'If an account exists with that email, a reset link has been sent.')
            return redirect('accounts:login')
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})


@never_cache
@ensure_csrf_cookie
def reset_password_view(request, uidb64, token):
    """Handle password reset with token."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully! Please log in.')
                return redirect('accounts:login')
        else:
            form = CustomSetPasswordForm(user)

        return render(request, 'accounts/reset_password.html', {'form': form})
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('accounts:forgot_password')


# =====================================================
# AUTHENTICATED USER VIEWS (profile, password change)
# =====================================================

@login_required
def profile_view(request):
    """Display and edit user profile."""
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update user fields
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.phone = request.POST.get('phone', user.phone)
            user.save()

            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(
            instance=profile,
            initial={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
            }
        )

    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': user,
        'profile': profile,
    })


@login_required
def change_password_view(request):
    """Handle password change."""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


# =====================================================
# ADMIN-ONLY USER MANAGEMENT VIEWS
# =====================================================

@login_required
@admin_required
def user_list_view(request):
    """Admin view to list and manage users."""
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')

    users = User.objects.select_related('profile').all()

    if query:
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(registration_number__icontains=query)
        )

    if role_filter:
        users = users.filter(role=role_filter)

    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)

    # Check if the current user can create new users
    can_create_users = request.user.role in ('super_admin', 'university_admin') or request.user.is_superuser

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'query': query,
        'role_filter': role_filter,
        'role_choices': User.ROLE_CHOICES,
        'can_create_users': can_create_users,
    })


@login_required
@admin_required
def user_detail_view(request, pk):
    """Admin view to see user details."""
    user = get_object_or_404(User.objects.select_related('profile'), pk=pk)

    # University Admin cannot view/manage Super Admin profiles
    if request.user.role == 'university_admin' and user.role == 'super_admin':
        messages.error(request, 'You do not have permission to view this user.')
        return redirect('accounts:user_list')

    activities = ActivityLog.objects.filter(user=user)[:20]

    # Check permissions for actions
    can_manage = _can_manage_user(request.user, user)

    return render(request, 'accounts/user_detail.html', {
        'viewed_user': user,
        'activities': activities,
        'can_manage': can_manage,
    })


@login_required
@senior_admin_required
def create_user_view(request):
    """
    Admin-only view to create new users.
    Only Super Admin and University Admin can access this.
    Role restrictions enforced at both UI and backend level.
    """
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST, creator=request.user)
        if form.is_valid():
            user = form.save()

            # Create user profile
            UserProfile.objects.get_or_create(user=user)

            # Log the action
            ActivityLog.objects.create(
                user=request.user,
                action='create_user',
                model_name='User',
                object_id=str(user.pk),
                details=f'Created user {user.get_full_name()} ({user.email}) with role {user.role_display}',
                ip_address=get_client_ip(request)
            )

            messages.success(request, f'User "{user.get_full_name()}" created successfully with role "{user.role_display}".')
            return redirect('accounts:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminUserCreationForm(creator=request.user)

    return render(request, 'accounts/create_user.html', {'form': form})


@login_required
@senior_admin_required
def admin_reset_password_view(request, pk):
    """Admin-only view to reset another user's password."""
    target_user = get_object_or_404(User, pk=pk)

    # Enforce: University Admin cannot reset Super Admin password
    if request.user.role == 'university_admin' and target_user.role == 'super_admin':
        messages.error(request, 'You do not have permission to reset this user\'s password.')
        return redirect('accounts:user_list')

    if request.method == 'POST':
        form = AdminPasswordResetForm(request.POST)
        if form.is_valid():
            target_user.set_password(form.cleaned_data['new_password1'])
            target_user.save()

            ActivityLog.objects.create(
                user=request.user,
                action='admin_reset_password',
                model_name='User',
                object_id=str(target_user.pk),
                details=f'Admin reset password for {target_user.get_full_name()} ({target_user.email})',
                ip_address=get_client_ip(request)
            )

            messages.success(request, f'Password for "{target_user.get_full_name()}" has been reset successfully.')
            return redirect('accounts:user_detail', pk=target_user.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminPasswordResetForm()

    return render(request, 'accounts/admin_reset_password.html', {
        'form': form,
        'target_user': target_user,
    })


@login_required
@admin_required
def toggle_user_active(request, pk):
    """Admin action to activate/deactivate a user."""
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)

        # Enforce: University Admin cannot toggle Super Admin
        if request.user.role == 'university_admin' and user.role == 'super_admin':
            messages.error(request, 'You do not have permission to modify this user.')
            return redirect('accounts:user_list')

        # Prevent self-deactivation
        if user.pk == request.user.pk:
            messages.error(request, 'You cannot deactivate your own account.')
            return redirect('accounts:user_list')

        user.is_active = not user.is_active
        user.save()

        status = 'activated' if user.is_active else 'deactivated'

        ActivityLog.objects.create(
            user=request.user,
            action=f'user_{status}',
            model_name='User',
            object_id=str(user.pk),
            details=f'{status.capitalize()} user {user.get_full_name()} ({user.email})',
            ip_address=get_client_ip(request)
        )

        messages.success(request, f'User {user.get_full_name()} has been {status}.')
    return redirect('accounts:user_list')


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _can_manage_user(admin_user, target_user):
    """Check if an admin can manage (edit/toggle/reset) a target user."""
    if admin_user.is_superuser or admin_user.role == 'super_admin':
        return True
    if admin_user.role == 'university_admin':
        # University Admin cannot manage Super Admin
        return target_user.role != 'super_admin'
    if admin_user.role == 'department_admin':
        # Department Admin can only view, not manage
        return False
    return False


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')
