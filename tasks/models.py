# tasks/models.py
from django.db import models
from django.utils import timezone
from django.conf import settings
from .managers import SoftDeleteManager


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    # soft-delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()  # отдаёт только «живые»

    class Meta:
        # ВАЖНО: никакого created_at здесь нет!
        ordering = ['id']

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=['is_deleted', 'deleted_at'])


class Task(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        IN_PROGRESS = 'in_progress', 'In progress'
        DONE = 'done', 'Done'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    deadline = models.DateField(null=True, blank=True)

    # HW13: optional category
    category = models.ForeignKey(
        Category,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='tasks',
    )

    # HW19: владельцe задачи
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='tasks',
    )

    def __str__(self) -> str:
        return self.title


class SubTask(models.Model):
    """Подзадача (HW13)."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Task.Status.choices, default=Task.Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    # HW19: владелец подзадачи (будем ставить тот же, что у task)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='subtasks',
    )

    def __str__(self) -> str:
        return f'{self.title} (task #{self.task_id})'
