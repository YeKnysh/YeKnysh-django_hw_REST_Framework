# django_hw_REST_Framework/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/tasks/', include('tasks.urls')),
    path('api/', include('api.urls')),
]
