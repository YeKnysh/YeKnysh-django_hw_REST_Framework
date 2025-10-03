# HW12 — Task Manager API (DRF)

## Запуск
1) python -m venv venv && venv\Scripts\activate   # (Windows)
2) pip install -r requirements.txt
3) python manage.py migrate
4) python manage.py runserver

## Эндпоинты
- POST /api/v1/tasks/create/ — создание задачи (title, description, status [new|in_progress|done], deadline YYYY-MM-DD)
- GET  /api/v1/tasks/        — список задач
- GET  /api/v1/tasks/<id>/   — детальная задача
- GET  /api/v1/tasks/stats/  — статистика (total, by_status, overdue)
- GET  /api/ping/            — технический пинг (DRF UI)

## Быстрая проверка (PyCharm HTTP Client)
Смотри файл `requests.http` в корне репозитория.
