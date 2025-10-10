# tasks/views.py
from django.utils import timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.db.models.functions import ExtractWeekDay  # ДЗ-14

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination  # ДЗ-14

# --- ДЗ-15 (Generic Views) ---
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend

# --- ДЗ-16 (ViewSet для категорий) ---
from rest_framework import viewsets, decorators

from tasks.models import Task, SubTask, Category
from tasks.serializers import (
    # ДЗ-16
    CategorySerializer,
    CategoryCreateSerializer,
    # ДЗ-12/13
    TaskListSerializer,
    TaskDetailSerializer,
    TaskCreateSerializer,
    SubTaskSerializer,
    SubTaskCreateSerializer,
)

# ---------- ДЗ-12: FBV по Task (без изменений) ----------

@api_view(['POST'])
def task_create(request):
    serializer = TaskCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def task_list(request):
    qs = Task.objects.all().order_by('id')
    return Response(TaskListSerializer(qs, many=True).data)


@api_view(['GET'])
def task_detail(request, pk: int):
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(TaskDetailSerializer(task).data)


@api_view(['GET'])
def task_stats(request):
    total = Task.objects.count()
    by_status_raw = Task.objects.values('status').annotate(count=Count('id'))
    by_status = {row['status']: row['count'] for row in by_status_raw}

    today = timezone.now().date()
    overdue = Task.objects.filter(deadline__lt=today).exclude(status=Task.Status.DONE).count()

    return Response({
        'total_tasks': total,
        'by_status': by_status,
        'overdue_tasks': overdue,
    })


# ---------- ДЗ-13: APIView по SubTask (обновлено в ДЗ-14 для пагинации/фильтров) ----------

class SubTaskPagination(PageNumberPagination):
    """ДЗ-14: простая страничная пагинация."""
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class SubTaskListCreateView(APIView):
    """
    GET  /api/v1/tasks/subtasks/?task=<id>&task_title=<str>&status=<str>&page=<n>
         — список подзадач (фильтры опциональны), пагинация по 5, сортировка по -created_at
    POST /api/v1/tasks/subtasks/
         — создать подзадачу
    """
    def get(self, request):
        qs = SubTask.objects.all()

        # ДЗ-13 (было): фильтр по id задачи
        task_id = request.query_params.get('task')
        if task_id:
            qs = qs.filter(task_id=task_id)

        # ДЗ-14: дополнительные фильтры
        task_title = request.query_params.get('task_title')
        if task_title:
            qs = qs.filter(task__title__icontains=task_title)

        status_param = request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        # ДЗ-14: сортировка и пагинация
        qs = qs.order_by('-created_at')
        paginator = SubTaskPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        data = SubTaskSerializer(page, many=True).data
        return paginator.get_paginated_response(data)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubTaskDetailUpdateDeleteView(APIView):
    """
    GET    /api/v1/tasks/subtasks/<pk>/
    PUT    /api/v1/tasks/subtasks/<pk>/
    PATCH  /api/v1/tasks/subtasks/<pk>/
    DELETE /api/v1/tasks/subtasks/<pk>/
    """
    def get(self, request, pk):
        st = get_object_or_404(SubTask, pk=pk)
        return Response(SubTaskSerializer(st).data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        st = get_object_or_404(SubTask, pk=pk)
        serializer = SubTaskCreateSerializer(st, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        st = get_object_or_404(SubTask, pk=pk)
        serializer = SubTaskCreateSerializer(st, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        st = get_object_or_404(SubTask, pk=pk)
        st.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------- ДЗ-14: список задач по дню недели (query param) ----------

class TaskByWeekdayView(APIView):
    """
    GET /api/v1/tasks/by-day/?day=<понедельник|вторник|...|monday|tuesday|...>
    Если day не передан или не распознан — вернём все задачи.
    День недели берётся из поля deadline.
    """
    RU = {
        'вс': 1, 'воскресенье': 1,
        'пн': 2, 'понедельник': 2,
        'вт': 3, 'вторник': 3,
        'ср': 4, 'среда': 4,
        'чт': 5, 'четверг': 5,
        'пт': 6, 'пятница': 6,
        'сб': 7, 'суббота': 7,
    }
    EN = {
        'sunday': 1, 'sun': 1,
        'monday': 2, 'mon': 2,
        'tuesday': 3, 'tue': 3,
        'wednesday': 4, 'wed': 4,
        'thursday': 5, 'thu': 5,
        'friday': 6, 'fri': 6,
        'saturday': 7, 'sat': 7,
    }

    def get(self, request):
        day_raw = request.query_params.get('day')
        qs = Task.objects.all()

        if day_raw:
            key = day_raw.strip().lower()
            weekday = self.RU.get(key) or self.EN.get(key)
            if weekday:
                # ExtractWeekDay: 1=Sunday ... 7=Saturday
                qs = qs.annotate(wd=ExtractWeekDay('deadline')).filter(wd=weekday)

        data = TaskDetailSerializer(qs.order_by('id'), many=True).data
        return Response(data, status=status.HTTP_200_OK)


# ===================== ДЗ-15: GENERIC VIEWS (параллельно к старым) =====================

class TaskGVListCreateView(ListCreateAPIView):
    """
    GET  /api/v1/tasks-gv/        — список задач (фильтр/поиск/сорт)
    POST /api/v1/tasks-gv/        — создать задачу
    """
    queryset = Task.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['status', 'deadline']              # ?status=in_progress&deadline=2025-10-10
    search_fields = ['title', 'description']               # ?search=отчёт
    ordering_fields = ['deadline', 'id', 'title']          # ?ordering=-deadline

    def get_serializer_class(self):
        return TaskCreateSerializer if self.request.method == 'POST' else TaskListSerializer


class TaskGVDetailView(RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/v1/tasks-gv/<pk>/"""
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer


class SubTaskGVListCreateView(ListCreateAPIView):
    """
    GET  /api/v1/tasks/subtasks-gv/  — список (фильтр/поиск/сорт)
    POST /api/v1/tasks/subtasks-gv/  — создать
    """
    queryset = SubTask.objects.select_related('task').all().order_by('-created_at', '-id')
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['task', 'status']                  # ?task=1&status=done
    search_fields = ['title', 'task__title']               # ?search=подзадача
    ordering_fields = ['created_at', 'id', 'title', 'status']  # без 'deadline' — его нет у SubTask

    def get_serializer_class(self):
        return SubTaskCreateSerializer if self.request.method == 'POST' else SubTaskSerializer


class SubTaskGVDetailView(RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/v1/tasks/subtasks-gv/<pk>/"""
    queryset = SubTask.objects.select_related('task').all()
    serializer_class = SubTaskSerializer


# ============ ДЗ-16: Category ViewSet (CRUD + soft-delete + count_tasks) ============

class CategoryViewSet(viewsets.ModelViewSet):
    """
    Маршруты (через DefaultRouter, подключён в tasks/urls.py):
      - GET    /api/v1/tasks/categories/
      - POST   /api/v1/tasks/categories/
      - GET    /api/v1/tasks/categories/<id>/
      - PATCH  /api/v1/tasks/categories/<id>/
      - PUT    /api/v1/tasks/categories/<id>/
      - DELETE /api/v1/tasks/categories/<id>/    <-- мягкое удаление

    Кастомный экшен:
      - GET    /api/v1/tasks/categories/<id>/count_tasks/
    """
    queryset = Category.objects.all().order_by('id')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CategoryCreateSerializer
        return CategorySerializer

    def destroy(self, request, *args, **kwargs):
        """Мягкое удаление: model.delete() помечает is_deleted=True."""
        instance = self.get_object()
        instance.delete()
        return Response(status=204)

    @decorators.action(detail=True, methods=['get'])
    def count_tasks(self, request, pk=None):
        """Количество задач, привязанных к категории."""
        category = self.get_object()
        count = category.tasks.count()
        return Response({'category_id': category.id, 'tasks_count': count})
