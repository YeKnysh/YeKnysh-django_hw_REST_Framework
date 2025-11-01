# tasks/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from tasks.views import (
    # whoami
    WhoAmIView,
    # FBV (HW12/14)
    task_create, task_list, task_detail, task_stats, TaskByWeekdayView,
    # APIView (HW13)
    SubTaskListCreateView, SubTaskDetailUpdateDeleteView,
    # Generic Views (HW15)
    TaskGVListCreateView, TaskGVDetailView,
    SubTaskGVListCreateView, SubTaskGVDetailView,
    # HW16
    CategoryViewSet,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    # ----- WHOAMI (JWT cookie) -----
    path('whoami/', WhoAmIView.as_view(), name='whoami'),

    # ----- ОСНОВНЫЕ РОУТЫ ДЛЯ TASK (GV: List/Create + Detail/Update/Delete) -----
    path('', TaskGVListCreateView.as_view(), name='task-list-create'),          # GET list / POST create
    path('<int:pk>/', TaskGVDetailView.as_view(), name='task-detail'),          # GET / PUT / PATCH / DELETE

    # Вспомогательные
    path('stats/', task_stats, name='task-stats'),
    path('by-day/', TaskByWeekdayView.as_view(), name='task-by-day'),

    # ----- SUBTASKS -----
    path('subtasks/', SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:pk>/', SubTaskDetailUpdateDeleteView.as_view(), name='subtask-udr'),

    # Generic Views (HW15) — альтернативные маршруты
    path('subtasks-gv/', SubTaskGVListCreateView.as_view(), name='subtask-gv-list-create'),
    path('subtasks-gv/<int:pk>/', SubTaskGVDetailView.as_view(), name='subtask-gv-detail'),

    # ----- СТАРЫЕ FBV ДЛЯ TASK (чтобы ничего не ломать) -----
    path('fbv/', task_list, name='task-list-fbv'),                  # GET
    path('fbv/create/', task_create, name='task-create-fbv'),       # POST
    path('fbv/<int:pk>/', task_detail, name='task-detail-fbv'),     # GET

    # ----- HW16: router (categories) -----
    path('', include(router.urls)),
]
