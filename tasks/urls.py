# tasks/urls.py
from django.urls import path
from tasks.views import task_create, task_list, task_detail, task_stats

urlpatterns = [
    path('', task_list, name='task-list'),                 # GET /api/v1/tasks/
    path('create/', task_create, name='task-create'),      # POST /api/v1/tasks/create/
    path('<int:pk>/', task_detail, name='task-detail'),    # GET /api/v1/tasks/1/
    path('stats/', task_stats, name='task-stats'),         # GET /api/v1/tasks/stats/
]
