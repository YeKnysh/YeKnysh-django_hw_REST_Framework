# tasks/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешает читать всем аутентифицированным,
    изменять — только владельцу объекта (или владельцу родительской task у SubTask).
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "owner", None)
        if owner is None and hasattr(obj, "task"):
            owner = getattr(obj.task, "owner", None)
        return owner is not None and owner == request.user
