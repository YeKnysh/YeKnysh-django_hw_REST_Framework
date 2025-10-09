from django.urls import path
from tasks.views import (
    task_create, task_list, task_detail, task_stats,          # было в ДЗ-12
    SubTaskListCreateView, SubTaskDetailUpdateDeleteView,     # новое для ДЗ-13
)

urlpatterns = [
    # ---- Task (как было) ----
    path('', task_list, name='task-list'),                      # GET  /api/v1/tasks/
    path('create/', task_create, name='task-create'),           # POST /api/v1/tasks/create/
    path('stats/', task_stats, name='task-stats'),              # GET  /api/v1/tasks/stats/
    path('<int:pk>/', task_detail, name='task-detail'),         # GET  /api/v1/tasks/1/

    # ---- SubTask (APIView) ----
    path('subtasks/', SubTaskListCreateView.as_view(), name='subtask-list-create'),            # GET/POST
    path('subtasks/<int:pk>/', SubTaskDetailUpdateDeleteView.as_view(), name='subtask-udr'),   # GET/PUT/PATCH/DELETE
]
