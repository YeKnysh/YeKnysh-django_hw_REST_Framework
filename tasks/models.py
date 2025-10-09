from django.db import models


class Category(models.Model):
    """Категория задачи (новое для ДЗ-13)."""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        IN_PROGRESS = 'in_progress', 'In progress'
        DONE = 'done', 'Done'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    deadline = models.DateField(null=True, blank=True)

    # Новое поле для ДЗ-13: опциональная категория (не ломает существующие данные)
    category = models.ForeignKey(
        Category,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='tasks'
    )

    def __str__(self) -> str:
        return self.title


class SubTask(models.Model):
    """Подзадача (новое для ДЗ-13)."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Task.Status.choices, default=Task.Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.title} (task #{self.task_id})'
