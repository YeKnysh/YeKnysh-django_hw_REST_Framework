from django.utils import timezone
from rest_framework import serializers

from tasks.models import Task, SubTask, Category


# ---------- SubTask ----------
class SubTaskSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SubTask
        fields = "__all__"


class SubTaskCreateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SubTask
        fields = "__all__"

    def create(self, validated_data):
        # owner будем выставлять в представлении; здесь просто создаём
        return SubTask.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field in ("task", "title", "status"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance


# ---------- Category ----------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name"]

    def _validate_unique_name(self, name, *, exclude_pk=None):
        qs = Category.objects.filter(name__iexact=name)
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        if qs.exists():
            raise serializers.ValidationError("Category with this name already exists.")

    def create(self, validated_data):
        name = validated_data.get("name")
        self._validate_unique_name(name)
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get("name", instance.name)
        self._validate_unique_name(name, exclude_pk=instance.pk)
        instance.name = name
        instance.save(update_fields=["name"])
        return instance


# ---------- Task ----------
class TaskListSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "status", "deadline", "owner"]


class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = "__all__"


class TaskCreateSerializer(serializers.ModelSerializer):
    # category выпадающий список
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.order_by("id"),
        allow_null=True,
        required=False,
    )
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate_deadline(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    class Meta:
        model = Task
        fields = ["title", "description", "status", "deadline", "category", "owner"]

    def create(self, validated_data):
        return Task.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field in ("title", "description", "status", "deadline", "category"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance
