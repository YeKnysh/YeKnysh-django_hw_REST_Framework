# tasks/managers.py
from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """
    Безопасный менеджер: если у модели нет поля is_deleted — вернём обычный QS,
    чтобы ничего не падало в ветках без soft-delete.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        # защитимся на случай модели без поля is_deleted
        if any(f.name == "is_deleted" for f in self.model._meta.fields):
            return qs.filter(is_deleted=False)
        return qs

    def all_with_deleted(self):
        # Полезно для админки/отладки
        return super().get_queryset()
