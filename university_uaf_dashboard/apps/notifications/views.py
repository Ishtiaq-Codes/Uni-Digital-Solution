"""
Notification views.
"""
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Notification


@login_required
def notification_list(request):
    """List all notifications for the current user."""
    notifications = Notification.objects.filter(recipient=request.user)

    filter_type = request.GET.get('type', '')
    if filter_type:
        notifications = notifications.filter(notification_type=filter_type)

    unread_only = request.GET.get('unread', '')
    if unread_only:
        notifications = notifications.filter(is_read=False)

    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)

    return render(request, 'notifications/list.html', {
        'notifications': notifications,
        'filter_type': filter_type,
    })


@login_required
def mark_read(request, pk):
    """Mark a single notification as read."""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()

    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect('notifications:list')


@login_required
def notification_dropdown(request):
    """AJAX endpoint for notification dropdown."""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:10]

    data = [{
        'id': str(n.id),
        'title': n.title,
        'message': n.message[:100],
        'type': n.notification_type,
        'is_read': n.is_read,
        'link': n.link,
        'created_at': n.created_at.strftime('%b %d, %Y %I:%M %p'),
    } for n in notifications]

    return JsonResponse({
        'notifications': data,
        'unread_count': Notification.objects.filter(recipient=request.user, is_read=False).count()
    })
