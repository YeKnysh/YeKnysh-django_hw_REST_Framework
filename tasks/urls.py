from django.urls import path, include
from rest_framework.routers import DefaultRouter

from tasks.views import (
    # ДЗ-12
    task_create, task_list, task_detail, task_stats,
    # ДЗ-13
    SubTaskListCreateView, SubTaskDetailUpdateDeleteView,
    # ДЗ-14
    TaskByWeekdayView,
    # ДЗ-15 (Generic Views, новые маршруты)
    TaskGVListCreateView, TaskGVDetailView,
    SubTaskGVListCreateView, SubTaskGVDetailView,
    # ДЗ-16 (ModelViewSet для категорий)
    CategoryViewSet,
)

# ---- ДЗ-16: router для категорий ----
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
# Результат: /api/v1/tasks/categories/  (list, create)
#            /api/v1/tasks/categories/<id>/  (retrieve, update, partial_update, destroy)
#            + кастомные actions из ViewSet (например, count_tasks)

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

    # ---- ДЗ-15: Generic Views (параллельные маршруты, прошлое не трогаем) ----
    path('tasks-gv/', TaskGVListCreateView.as_view(), name='task-gv-list-create'),             # GET/POST
    path('tasks-gv/<int:pk>/', TaskGVDetailView.as_view(), name='task-gv-detail'),             # GET/PUT/PATCH/DELETE
    path('subtasks-gv/', SubTaskGVListCreateView.as_view(), name='subtask-gv-list-create'),    # GET/POST
    path('subtasks-gv/<int:pk>/', SubTaskGVDetailView.as_view(), name='subtask-gv-detail'),    # GET/PUT/PATCH/DELETE

    # ---- ДЗ-16: подключаем router (категории) ----
    path('', include(router.urls)),
]
