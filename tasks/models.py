# tasks/models.py
from django.db import models
from django.utils import timezone

from .managers import SoftDeleteManager


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    # soft-delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()  # по умолчанию отдаёт только «живые»

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        """Мягкое удаление: помечаем запись удалённой, физически не удаляем."""
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

    # НОВОЕ: привязка к категории (необязательная, чтобы не ломать старые данные)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )

    def __str__(self):
        return self.title


class SubTask(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        IN_PROGRESS = 'in_progress', 'In progress'
        DONE = 'done', 'Done'

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    # у тебя это поле используется для сортировки/пагинации — оставляем
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.task_id}: {self.title}'
