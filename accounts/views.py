from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import RegisterSerializer, LoginSerializer


def _set_auth_cookies(response, access, refresh):
    cfg = settings.SIMPLE_JWT
    access_max_age = int(cfg["ACCESS_TOKEN_LIFETIME"].total_seconds())
    refresh_max_age = int(cfg["REFRESH_TOKEN_LIFETIME"].total_seconds())

    response.set_cookie(
        key=cfg["AUTH_COOKIE"],
        value=str(access),
        max_age=access_max_age,
        httponly=cfg["AUTH_COOKIE_HTTP_ONLY"],
        secure=cfg["AUTH_COOKIE_SECURE"],
        samesite=cfg["AUTH_COOKIE_SAMESITE"],
        path=cfg["AUTH_COOKIE_PATH"],
    )
    response.set_cookie(
        key=cfg["AUTH_COOKIE_REFRESH"],
        value=str(refresh),
        max_age=refresh_max_age,
        httponly=cfg["AUTH_COOKIE_HTTP_ONLY"],
        secure=cfg["AUTH_COOKIE_SECURE"],
        samesite=cfg["AUTH_COOKIE_SAMESITE"],
        path=cfg["AUTH_COOKIE_PATH"],
    )
    return response


def _clear_auth_cookies(response):
    cfg = settings.SIMPLE_JWT
    for key in (cfg["AUTH_COOKIE"], cfg["AUTH_COOKIE_REFRESH"]):
        response.delete_cookie(
            key=key,
            path=cfg["AUTH_COOKIE_PATH"],
            samesite=cfg["AUTH_COOKIE_SAMESITE"],
        )
    return response


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Register new user with password validation and hashing.
        """
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        data = {"id": user.id, "username": user.username, "email": user.email}
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Issue JWT pair and store tokens in httpOnly cookies.
        Also returns tokens in body for Postman проверки.
        """
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        payload = {
            "access": str(access),
            "refresh": str(refresh),
            "user": {"id": user.id, "username": user.username, "email": user.email},
            "issued_at": timezone.now().isoformat(),
        }
        resp = Response(payload, status=status.HTTP_200_OK)
        _set_auth_cookies(resp, access, refresh)
        return resp


class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Refresh using cookie if body not provided.
        With ROTATE_REFRESH_TOKENS=True we set new refresh cookie and blacklist old.
        """
        cfg = settings.SIMPLE_JWT
        if "refresh" not in request.data:
            cookie_refresh = request.COOKIES.get(cfg["AUTH_COOKIE_REFRESH"])
            if cookie_refresh:
                request.data["refresh"] = cookie_refresh  # mutate for parent view
        response = super().post(request, *args, **kwargs)
        # если refresh был валидный — parent view вернет новый access и, при ротации, refresh
        new_access = response.data.get("access")
        new_refresh = response.data.get("refresh")
        if new_access:
            _set_auth_cookies(response, new_access, new_refresh or request.data.get("refresh"))
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Blacklist current refresh token (from cookie) and clear cookies.
        """
        cfg = settings.SIMPLE_JWT
        token = request.COOKIES.get(cfg["AUTH_COOKIE_REFRESH"])
        if token:
            try:
                RefreshToken(token).blacklist()
            except Exception:
                # уже отозван или невалиден — просто чистим куки
                pass
        resp = Response({"detail": "Logged out."}, status=status.HTTP_200_OK)
        _clear_auth_cookies(resp)
        return resp
