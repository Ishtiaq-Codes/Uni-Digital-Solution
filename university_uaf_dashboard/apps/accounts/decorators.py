"""
Role-based access control decorators and mixins.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden


def role_required(*roles):
    """Decorator to restrict view access to specific roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in roles and not request.user.is_superuser:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard:home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator to restrict access to admin roles only."""
    return role_required('super_admin', 'university_admin', 'department_admin')(view_func)


def senior_admin_required(view_func):
    """Decorator to restrict access to Super Admin and University Admin only.
    Used for user creation and high-level user management."""
    return role_required('super_admin', 'university_admin')(view_func)


def faculty_required(view_func):
    """Decorator to restrict access to faculty only."""
    return role_required('faculty', 'super_admin', 'university_admin')(view_func)


def student_required(view_func):
    """Decorator to restrict access to students only."""
    return role_required('ug_student', 'pg_student')(view_func)


def ug_student_required(view_func):
    """Decorator to restrict access to undergraduate students only."""
    return role_required('ug_student', 'super_admin', 'university_admin')(view_func)


def pg_student_required(view_func):
    """Decorator to restrict access to postgraduate students only."""
    return role_required('pg_student', 'super_admin', 'university_admin')(view_func)


def qec_required(view_func):
    """Decorator to restrict access to QEC officers only."""
    return role_required('qec_officer', 'super_admin', 'university_admin')(view_func)


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for class-based views requiring specific roles."""
    allowed_roles = []

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('dashboard:home')


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['super_admin', 'university_admin', 'department_admin']


class SeniorAdminRequiredMixin(RoleRequiredMixin):
    """Mixin for views restricted to Super Admin and University Admin."""
    allowed_roles = ['super_admin', 'university_admin']


class FacultyRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['faculty', 'super_admin', 'university_admin']


class StudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['ug_student', 'pg_student']
