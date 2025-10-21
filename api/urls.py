from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def ping(request):
    return Response({'status': 'ok'})

urlpatterns = [
    path('api/v1/tasks/', include('tasks.urls')),
    path('api/ping/', ping, name='ping'),
]
