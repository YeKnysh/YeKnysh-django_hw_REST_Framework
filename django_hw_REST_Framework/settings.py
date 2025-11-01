"""
Django settings for django_hw_REST_Framework project.
"""

from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure--670u0hjvk8x--p6gx@l!6_%-ttbwf=q*@xbl%%)7ydxml)mo^'
DEBUG = True
ALLOWED_HOSTS: list[str] = []

# --- DRF + глобальная пагинация (HW17: CursorPagination) ---
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # читаем access из httpOnly cookie, если нет Authorization header
        'accounts.authentication.CookieJWTAuthentication',
        # fallback по заголовку Authorization: Bearer <access>
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Без «page/limit» в урле, курсоры безопаснее не “светят” параметры
    'DEFAULT_PAGINATION_CLASS': 'tasks.pagination.DefaultCursorPagination',
    'PAGE_SIZE': 5,
}

INSTALLED_APPS = [
    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third-party
    'rest_framework',
    'django_filters',          # <- для фильтров в Generic Views

    # local apps
    'api',
    'tasks.apps.TasksConfig',  # <- важно для срабатывания signals в ready()
    'drf_yasg',
    'accounts',  # <- наш app для auth эндпоинтов/классов

    # blacklist refresh-токенов (HW20)
    'rest_framework_simplejwt.token_blacklist',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_hw_REST_Framework.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_hw_REST_Framework.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===================== HW17: ЛОГИРОВАНИЕ =====================
LOGS_DIR = BASE_DIR / 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
        'http': {
            'format': '[{asctime}] {levelname} {message}',
            'style': '{',
        },
        'db': {
            'format': '[{asctime}] {levelname} SQL: {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'http_file': {
            'class': 'logging.FileHandler',
            'filename': str(LOGS_DIR / 'http_logs.log'),
            'encoding': 'utf-8',
            'formatter': 'http',
        },
        'db_file': {
            'class': 'logging.FileHandler',
            'filename': str(LOGS_DIR / 'db_logs.log'),
            'encoding': 'utf-8',
            'formatter': 'db',
        },
    },

    'loggers': {
        'django.server': {
            'handlers': ['console', 'http_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['db_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

# --- Email (HW21): консольный backend, чтобы письма печатались в runserver ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Task Manager <noreply@localhost>'

# --- JWT lifetimes + rotation/blacklist + cookie-ключи (HW20) ---
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),

    # HW20: при рефреше выдаём новый refresh и заносим старый в blacklist
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    # используем общий SECRET_KEY как SIGNING_KEY
    'SIGNING_KEY': SECRET_KEY,

    # имена и параметры httpOnly cookie (access/refresh)
    'AUTH_COOKIE': 'access',
    'AUTH_COOKIE_REFRESH': 'refresh',
    'AUTH_COOKIE_SECURE': False,      # True на HTTPS-проде
    'AUTH_COOKIE_HTTP_ONLY': True,
    'AUTH_COOKIE_SAMESITE': 'Lax',    # 'None' если кросс-домен и HTTPS
    'AUTH_COOKIE_PATH': '/',
}
