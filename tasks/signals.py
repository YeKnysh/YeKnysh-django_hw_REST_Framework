# tasks/signals.py
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Task


@receiver(pre_save, sender=Task)
def _remember_old_status(sender, instance: Task, **kwargs):
    """
    Before saving an existing Task, remember its previous status.
    We store it on the instance to compare in post_save.
    """
    if not instance.pk:
        instance._old_status = None
        return
    try:
        old = sender.objects.only('status').get(pk=instance.pk)
        instance._old_status = old.status
    except sender.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Task)
def _notify_on_status_change(sender, instance: Task, created: bool, **kwargs):
    """
    After saving a Task:
      - skip on create;
      - send email only if status actually changed.
    """
    if created:
        return

    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status

    # no change → no email
    if old_status == new_status:
        return

    # owner must exist and have email
    owner = getattr(instance, 'owner', None)
    if not owner or not owner.email:
        return

    subject = f"[Task status changed] {instance.title}"
    message = (
        f"Hello, {owner.username}!\n\n"
        f"Your task '{instance.title}' has changed its status:\n"
        f"{old_status or '—'} → {new_status}\n\n"
        f"Task ID: {instance.id}"
    )

    # prints to console via EMAIL_BACKEND=console
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost'),
            recipient_list=[owner.email],
            fail_silently=True,  # не валим сохранение, если почта недоступна
        )
    except Exception:
        # крайний случай: вообще не мешаем бизнес-логике
        pass
