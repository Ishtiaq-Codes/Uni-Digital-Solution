"""
Custom template tags for the dashboard.
"""
from django import template

register = template.Library()


@register.filter
def get_role_color(role):
    """Return Tailwind CSS color class for a role."""
    colors = {
        'super_admin': 'bg-red-100 text-red-800',
        'university_admin': 'bg-purple-100 text-purple-800',
        'department_admin': 'bg-blue-100 text-blue-800',
        'faculty': 'bg-emerald-100 text-emerald-800',
        'ug_student': 'bg-indigo-100 text-indigo-800',
        'pg_student': 'bg-cyan-100 text-cyan-800',
        'qec_officer': 'bg-amber-100 text-amber-800',
    }
    return colors.get(role, 'bg-slate-100 text-slate-800')


@register.filter
def get_status_color(status):
    """Return Tailwind CSS color class for a status."""
    colors = {
        'pending': 'bg-amber-100 text-amber-800',
        'approved': 'bg-emerald-100 text-emerald-800',
        'rejected': 'bg-red-100 text-red-800',
        'paid': 'bg-emerald-100 text-emerald-800',
        'revision_requested': 'bg-blue-100 text-blue-800',
    }
    return colors.get(status, 'bg-slate-100 text-slate-800')


@register.filter
def percentage(value, total):
    """Calculate percentage."""
    try:
        return round((value / total) * 100, 1)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0


@register.simple_tag
def sidebar_active(request, pattern):
    """Return active class if current path matches pattern."""
    import re
    if re.search(pattern, request.path):
        return 'bg-indigo-700 text-white'
    return 'text-slate-300 hover:bg-slate-800 hover:text-white'
