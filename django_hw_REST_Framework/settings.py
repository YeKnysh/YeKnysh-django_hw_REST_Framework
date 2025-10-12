"""
Django settings for django_hw_REST_Framework project.
"""

from pathlib import Path
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
    # Без «page/limit» в урле, курсоры безопаснее не “светят” параметры
    'DEFAULT_PAGINATION_CLASS': 'tasks.pagination.DefaultCursorPagination',
    'PAGE_SIZE': 6,
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
    'tasks',
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
os.makedirs(LOGS_DIR, exist_ok=True)   # безопасно создадим папку, если нет

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
        'http': {
            # запросы runserver (django.server) печатает уже готовыми строками — оставляем компактный формат
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
        # 1) Логи запущенного сервера (запросы/статусы) -> консоль + файл logs/http_logs.log
        'django.server': {
            'handlers': ['console', 'http_file'],
            'level': 'INFO',
            'propagate': False,
        },
        # 2) SQL-запросы -> файл logs/db_logs.log
        'django.db.backends': {
            'handlers': ['db_file'],
            'level': 'DEBUG',     # DEBUG — чтобы писать текст SQL
            'propagate': False,
        },
        # Базовый логгер (на всё остальное) — в консоль
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
