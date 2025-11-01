# django_hw_REST_Framework/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Swagger / Redoc
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="Task Manager API",
        default_version='v1',
        description="HW12–HW19: JWT, permissions, pagination, categories, whoami",
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # твои API
    path('api/v1/tasks/', include('tasks.urls')),
    path('api/', include('api.urls')),
    path("api/v1/auth/", include("accounts.urls", namespace="accounts")),

    # JWT
    path('api/v1/auth/jwt/create/',  TokenObtainPairView.as_view(), name='jwt_create'),
    path('api/v1/auth/jwt/refresh/', TokenRefreshView.as_view(),   name='jwt_refresh'),
    path('api/v1/auth/jwt/verify/',  TokenVerifyView.as_view(),    name='jwt_verify'),

    # Docs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/',   schema_view.with_ui('redoc',   cache_timeout=0), name='schema-redoc'),
    path('api/schema.json', schema_view.without_ui(cache_timeout=0),  name='schema-json'),
    path('api/schema.yaml', schema_view.without_ui(cache_timeout=0),  name='schema-yaml'),
]
