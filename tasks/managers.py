# tasks/managers.py
from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet с поддержкой мягкого удаления и выборок alive/deleted."""

    def alive(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def delete(self):
        """
        МЯГКОЕ удаление для bulk-операций:
        Category.all_objects.filter(...).delete()  -> is_deleted=True, deleted_at=now()
        """
        return super().update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """Физическое удаление (если когда-нибудь понадобится)."""
        return super().delete()


class SoftDeleteManager(models.Manager):
    """
    Менеджер по умолчанию — скрывает мягко удалённые записи.
    Возвращает наш кастомный SoftDeleteQuerySet, чтобы работали .delete(), .alive(), .deleted().
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def all_with_deleted(self):
        """Вернуть все записи, включая удалённые (удобно для админки/отладки)."""
        return SoftDeleteQuerySet(self.model, using=self._db).all()

    def deleted_only(self):
        """Вернуть только удалённые записи."""
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()
