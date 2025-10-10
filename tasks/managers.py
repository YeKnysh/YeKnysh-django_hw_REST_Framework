# tasks/managers.py
from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """Менеджер по умолчанию — возвращает только НЕудалённые записи."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False).select_related()

    def all_with_deleted(self):
        # иногда полезно (админки, отладка)
        return super().get_queryset()
