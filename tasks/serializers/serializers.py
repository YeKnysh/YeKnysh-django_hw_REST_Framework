# tasks/serializers.py
from django.utils import timezone
from rest_framework import serializers

from tasks.models import Task, SubTask, Category


# ---------- SubTask ----------
class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = "__all__"


class SubTaskCreateSerializer(serializers.ModelSerializer):
    # ДЗ-13.1: только для чтения
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubTask
        fields = "__all__"

    # ДЗ-13: переопределяем create/update
    def create(self, validated_data):
        return SubTask.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field in ("task", "title", "status"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance


# ---------- Category ----------
class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Для create/update — пишем только name.
    (Так безопасно и для ветки без soft-delete, и для ветки с ним.)
    """
    class Meta:
        model = Category
        fields = ["name"]  # НЕ '__all__' — чтобы не дать писать служебные поля

    # ДЗ-13.2: проверка уникальности имени (case-insensitive) для create/update
    def validate_name(self, value: str):
        qs = Category.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Category with this name already exists.")
        return value


# ---------- Task (ДЗ-12 + расширения) ----------
class TaskListSerializer(serializers.ModelSerializer):
    # как было в ДЗ-12
    class Meta:
        model = Task
        fields = ["id", "title", "status", "deadline"]


class TaskDetailSerializer(serializers.ModelSerializer):
    # ДЗ-13.3: вложенные подзадачи (read_only)
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = "__all__"   # + включит объявленное поле subtasks


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Создание/обновление Task.
    - ДЗ-13.4: валидация дедлайна (не в прошлом)
    - Безопасный queryset у category (фикс для ДЗ-17 и ListCreateAPIView формы)
    """
    # принудительно задаём безопасный порядок для выпадающего списка
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.order_by("id"),
        allow_null=True,
        required=False,
    )

    def validate_deadline(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    class Meta:
        model = Task
        # как в ДЗ-12 + возможность указать category (необязательно)
        fields = ["title", "description", "status", "deadline", "category"]

    # ДЗ-13: переопределяем create/update
    def create(self, validated_data):
        return Task.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field in ("title", "description", "status", "deadline", "category"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance
