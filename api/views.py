from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def ping(request):
    return Response({'status': 'ok'})
# api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])   # ping пусть открытый, чтобы всегда быстро проверить сервер
def ping(request):
    return Response({'status': 'ok'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])   # здесь требуем JWT — это и есть проверка текущего пользователя
def whoami(request):
    u = request.user
    return Response({
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'is_staff': u.is_staff,
        # при желании можно добавить first_name/last_name и т.п.
    })
