"""
Notification signals - auto-create notifications on key events.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='fees.FeeVoucher')
def notify_voucher_status(sender, instance, created, **kwargs):
    """Notify student when voucher status changes."""
    from .models import Notification
    if created:
        Notification.create_notification(
            recipient=instance.student,
            title='New Fee Voucher Generated',
            message=f'Fee voucher {instance.voucher_number} has been generated. Amount: Rs. {instance.amount}',
            notification_type='fee',
            link=f'/fees/{instance.pk}/'
        )
    elif instance.status in ['approved', 'rejected']:
        Notification.create_notification(
            recipient=instance.student,
            title=f'Fee Voucher {instance.status.title()}',
            message=f'Your fee voucher {instance.voucher_number} has been {instance.status}.',
            notification_type='fee',
            link=f'/fees/{instance.pk}/'
        )


@receiver(post_save, sender='form_manager.FormSubmission')
def notify_form_status(sender, instance, created, **kwargs):
    """Notify student when form submission status changes."""
    from .models import Notification
    if not created and instance.status != 'pending':
        Notification.create_notification(
            recipient=instance.student,
            title=f'Form {instance.status.replace("_", " ").title()}',
            message=f'Your submission for "{instance.template.title}" has been {instance.status.replace("_", " ")}.',
            notification_type='form',
            link=f'/forms/submission/{instance.pk}/'
        )


@receiver(post_save, sender='university.Announcement')
def notify_announcement(sender, instance, created, **kwargs):
    """Notify users about new announcements."""
    if created and instance.is_active:
        from .models import Notification
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(is_active=True)
        Notification.notify_all(
            recipients=users,
            title='New Announcement',
            message=instance.title,
            notification_type='announcement',
            link=f'/university/announcements/{instance.pk}/'
        )
