# tasks/views.py
from django.utils import timezone
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from tasks.models import Task
from tasks.serializers import (
    TaskListSerializer, TaskDetailSerializer, TaskCreateSerializer
)

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
    overdue = Task.objects.filter(deadline__lt=today)\
                          .exclude(status=Task.Status.DONE).count()

    return Response({
        'total_tasks': total,
        'by_status': by_status,
        'overdue_tasks': overdue,
    })
