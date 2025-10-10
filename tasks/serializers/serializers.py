from django.utils import timezone
from rest_framework import serializers

from tasks.models import Task, SubTask, Category


# ---------- SubTask ----------
class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = '__all__'


class SubTaskCreateSerializer(serializers.ModelSerializer):
    # ДЗ-13.1: делаем только для чтения
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubTask
        fields = '__all__'


# ---------- Category (для ДЗ-16: ViewSet + soft-delete) ----------
class CategorySerializer(serializers.ModelSerializer):
    """
    Для list/retrieve. Поля soft-delete только для чтения.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_deleted', 'deleted_at']
        read_only_fields = ['is_deleted', 'deleted_at']


class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Для create/update. Пишем только name.
    """
    class Meta:
        model = Category
        fields = ['name']   # важно НЕ давать писать is_deleted/deleted_at

    # ДЗ-13.2 (ранее): проверка уникальности имени (case-insensitive)
    # Работает и для create, и для update.
    def validate_name(self, value: str):
        qs = Category.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Category with this name already exists.')
        return value


# ---------- Task (ДЗ-12 + расширения) ----------
class TaskListSerializer(serializers.ModelSerializer):
    # Сохраняем как было в ДЗ-12 (id, title, status, deadline)
    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'deadline']


class TaskDetailSerializer(serializers.ModelSerializer):
    # ДЗ-13.3: вложенные подзадачи (read_only)
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        # '__all__' + объявленное поле `subtasks` попадёт в вывод
        fields = '__all__'


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Создание/обновление Task. ДЗ-13.4: валидация дедлайна (не в прошлом).
    Поле category оставляем как PK (как и раньше), оно необязательно (null/blank).
    """
    def validate_deadline(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError('Deadline cannot be in the past.')
        return value

    class Meta:
        model = Task
        # как в ДЗ-12 + даём возможность указать категорию (необязательно)
        fields = ['title', 'description', 'status', 'deadline', 'category']
