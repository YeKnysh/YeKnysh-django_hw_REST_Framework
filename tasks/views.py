# tasks/views.py
from django.utils import timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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


# ---------- ДЗ-13: APIView по SubTask ----------

class SubTaskListCreateView(APIView):
    """
    GET /api/v1/tasks/subtasks/?task=<id>  — список подзадач (опционально фильтр по задаче)
    POST /api/v1/tasks/subtasks/           — создать подзадачу
    """
    def get(self, request):
        qs = SubTask.objects.all().order_by('id')
        task_id = request.query_params.get('task')
        if task_id:
            qs = qs.filter(task_id=task_id)
        return Response(SubTaskSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubTaskDetailUpdateDeleteView(APIView):
    """
    GET    /api/v1/tasks/subtasks/<pk>/ — деталь
    PUT    /api/v1/tasks/subtasks/<pk>/ — полное обновление
    PATCH  /api/v1/tasks/subtasks/<pk>/ — частичное обновление
    DELETE /api/v1/tasks/subtasks/<pk>/ — удалить
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
