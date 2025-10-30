# api/urls.py
from django.urls import path
from .views import ping, whoami

urlpatterns = [
    path('ping/', ping, name='ping'),                     # -> /api/ping/
    path('v1/auth/whoami/', whoami, name='whoami'),       # -> /api/v1/auth/whoami/
]
