# tasks/views.py
from django.utils import timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.db.models.functions import ExtractWeekDay  # <-- ДЗ-14: извлекаем день недели из даты

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination  # <-- ДЗ-14: пагинация

from tasks.models import Task, SubTask
from tasks.serializers import (
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
