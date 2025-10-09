from django.urls import path
from tasks.views import (
    # ДЗ-12
    task_create, task_list, task_detail, task_stats,
    # ДЗ-13
    SubTaskListCreateView, SubTaskDetailUpdateDeleteView,
    # ДЗ-14
    TaskByWeekdayView,
)

urlpatterns = [
    # ---- Task (ДЗ-12) ----
    path('', task_list, name='task-list'),                       # GET  /api/v1/tasks/
    path('create/', task_create, name='task-create'),            # POST /api/v1/tasks/create/
    path('stats/', task_stats, name='task-stats'),               # GET  /api/v1/tasks/stats/
    path('<int:pk>/', task_detail, name='task-detail'),          # GET  /api/v1/tasks/1/

    # ---- Task by weekday (ДЗ-14) ----
    path('by-day/', TaskByWeekdayView.as_view(), name='task-by-day'),  # GET /api/v1/tasks/by-day/?day=tuesday

    # ---- SubTask (ДЗ-13) ----
    path('subtasks/', SubTaskListCreateView.as_view(), name='subtask-list-create'),            # GET/POST
    path('subtasks/<int:pk>/', SubTaskDetailUpdateDeleteView.as_view(), name='subtask-udr'),   # GET/PUT/PATCH/DELETE
]
