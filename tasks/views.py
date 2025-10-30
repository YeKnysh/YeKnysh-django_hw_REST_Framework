from django.utils import timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.db.models.functions import ExtractWeekDay

from rest_framework import status, viewsets, decorators, filters as drf_filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView
)
from django_filters.rest_framework import DjangoFilterBackend

from tasks.pagination import DefaultCursorPagination
from tasks.models import Task, SubTask, Category
from tasks.serializers import (
    CategorySerializer, CategoryCreateSerializer,
    TaskListSerializer, TaskDetailSerializer, TaskCreateSerializer,
    SubTaskSerializer, SubTaskCreateSerializer,
)
from tasks.permissions import IsOwnerOrReadOnly


# ---------- доказательный эндпоинт: кто я ----------
class WhoAmIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response(
            {"id": u.id, "username": u.username, "email": u.email, "is_staff": u.is_staff},
            status=status.HTTP_200_OK,
        )


# ---------- HW12: FBV Task ----------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def task_create(request):
    serializer = TaskCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_list(request):
    qs = Task.objects.filter(owner=request.user).order_by('-id')
    paginator = DefaultCursorPagination()
    page = paginator.paginate_queryset(qs, request)
    data = TaskListSerializer(page, many=True).data
    return paginator.get_paginated_response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_detail(request, pk: int):
    task = get_object_or_404(Task.objects.filter(owner=request.user), pk=pk)
    return Response(TaskDetailSerializer(task).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_stats(request):
    base_qs = Task.objects.filter(owner=request.user)
    total = base_qs.count()
    by_status_raw = base_qs.values('status').annotate(count=Count('id'))
    by_status = {row['status']: row['count'] for row in by_status_raw}

    today = timezone.now().date()
    overdue = base_qs.filter(deadline__lt=today).exclude(status=Task.Status.DONE).count()

    return Response(
        {
            'total_tasks': total,
            'by_status': by_status,
            'overdue_tasks': overdue,
        },
        status=status.HTTP_200_OK,
    )


# ---------- HW13: APIView SubTask (+ HW14 filters/pagination) ----------
class SubTaskPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class SubTaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = SubTask.objects.filter(task__owner=request.user)

        task_id = request.query_params.get('task')
        if task_id:
            qs = qs.filter(task_id=task_id)

        task_title = request.query_params.get('task_title')
        if task_title:
            qs = qs.filter(task__title__icontains=task_title)

        status_param = request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        qs = qs.order_by('-created_at', '-id')
        paginator = SubTaskPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        data = SubTaskSerializer(page, many=True).data
        return paginator.get_paginated_response(data)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.validated_data.get('task')
            if task.owner_id != request.user.id:
                return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubTaskDetailUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, pk, user):
        return get_object_or_404(
            SubTask.objects.select_related('task').filter(task__owner=user),
            pk=pk,
        )

    def get(self, request, pk):
        st = self._get(pk, request.user)
        return Response(SubTaskSerializer(st).data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        st = self._get(pk, request.user)
        serializer = SubTaskCreateSerializer(st, data=request.data)
        if serializer.is_valid():
            new_task = serializer.validated_data.get('task', st.task)
            if new_task.owner_id != request.user.id:
                return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        st = self._get(pk, request.user)
        serializer = SubTaskCreateSerializer(st, data=request.data, partial=True)
        if serializer.is_valid():
            new_task = serializer.validated_data.get('task', st.task)
            if new_task.owner_id != request.user.id:
                return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        st = self._get(pk, request.user)
        st.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------- HW14: tasks by weekday ----------
class TaskByWeekdayView(APIView):
    permission_classes = [IsAuthenticated]

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
        qs = Task.objects.filter(owner=request.user)

        if day_raw:
            key = day_raw.strip().lower()
            weekday = self.RU.get(key) or self.EN.get(key)
            if weekday:
                qs = qs.annotate(wd=ExtractWeekDay('deadline')).filter(wd=weekday)

        data = TaskDetailSerializer(qs.order_by('id'), many=True).data
        return Response(data, status=status.HTTP_200_OK)


# ---------- HW15: Generic Views ----------
class TaskGVListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['deadline', 'id', 'title']

    def get_queryset(self):
        # показываем только свои задачи
        return Task.objects.filter(owner=self.request.user).order_by('-id')

    def get_serializer_class(self):
        return TaskCreateSerializer if self.request.method == 'POST' else TaskListSerializer

    def perform_create(self, serializer):
        # фиксируем владельца создаваемой задачи
        serializer.save(owner=self.request.user)


class TaskGVDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = TaskDetailSerializer

    def get_queryset(self):
        # доступ только к своим объектам
        return Task.objects.filter(owner=self.request.user)


class SubTaskGVListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['task', 'status']
    search_fields = ['title', 'task__title']
    ordering_fields = ['created_at', 'id', 'title', 'status']

    def get_queryset(self):
        # список только подзадач своих задач
        return (
            SubTask.objects
            .select_related('task')
            .filter(task__owner=self.request.user)
            .order_by('-created_at', '-id')
        )

    def get_serializer_class(self):
        return SubTaskCreateSerializer if self.request.method == 'POST' else SubTaskSerializer

    def perform_create(self, serializer):
        # запрещаем создавать подзадачу на чужой задаче
        task = serializer.validated_data.get('task')
        if task and task.owner_id != self.request.user.id:
            raise PermissionDenied("You cannot create a subtask for a foreign task.")
        serializer.save(owner=self.request.user)


class SubTaskGVDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = SubTaskSerializer

    def get_queryset(self):
        # доступ только к подзадачам своих задач
        return SubTask.objects.select_related('task').filter(task__owner=self.request.user)

    def perform_update(self, serializer):
        # запрещаем переносить подзадачу на чужую задачу
        new_task = serializer.validated_data.get('task')
        if new_task and new_task.owner_id != self.request.user.id:
            raise PermissionDenied("You cannot reassign a subtask to a foreign task.")
        serializer.save()


# ---------- HW16: Category ViewSet ----------
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('id')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CategoryCreateSerializer
        return CategorySerializer

    @decorators.action(detail=True, methods=['get'])
    def count_tasks(self, request, pk=None):
        category = self.get_object()
        return Response({'category_id': category.id, 'tasks_count': category.tasks.count()}, status=status.HTTP_200_OK)
