# Task Manager API — HW12…HW17 (DRF)

## Запуск
1) `python -m venv venv && venv\Scripts\activate`  *(Windows)*
2) `pip install -r requirements.txt`
3) `python manage.py migrate`
4) `python manage.py runserver`

Тех. проверка: `GET http://127.0.0.1:8000/api/ping/` → `{"status":"ok"}`.

---

## Эндпоинты

### HW12 — базовые задачи
- `POST /api/v1/tasks/create/` — создать задачу (`title`, `description`, `status:[new|in_progress|done]`, `deadline:YYYY-MM-DD`)
- `GET  /api/v1/tasks/` — список задач
- `GET  /api/v1/tasks/<id>/` — детальная задача
- `GET  /api/v1/tasks/stats/` — агрегаты (total, by_status, overdue)

### HW13 — сериализаторы и SubTask (APIView)
- В `TaskDetail` возвращаются вложенные `subtasks` (read-only).
- Валидация: `deadline` не может быть в прошлом.
- SubTask (APIView):
  - `GET/POST    /api/v1/tasks/subtasks/`
  - `GET/PUT/PATCH/DELETE /api/v1/tasks/subtasks/<id>/`

**Важно (ресабмит HW13 — Задание 2):**  
Переопределены методы `create`/`update` в `CategoryCreateSerializer` с проверкой уникальности имени (case-insensitive).  
- Эндпоинты категорий (ViewSet):  
  - `GET/POST    /api/v1/tasks/categories/`  
  - `GET/PATCH/PUT/DELETE /api/v1/tasks/categories/<id>/`
- Ожидаемое поведение: повторный `POST` с тем же `name` → **400** (ошибка валидации).

### HW14 — параметры и пагинация
- `GET /api/v1/tasks/by-day/?day=<понедельник|вторник|...|monday|tuesday|...>` — задачи по дню недели (из `deadline`), без параметра — все.
- `GET /api/v1/tasks/subtasks/?page=1&task=<id>&task_title=<str>&status=<new|in_progress|done>`  
  Пагинация 5 на страницу, сортировка по `-created_at`.

### HW15 — Generic Views (альтернативные маршруты)
- Tasks (GV):
  - `GET/POST  /api/v1/tasks-gv/?search=..&status=..&ordering=..`
  - `GET/PUT/PATCH/DELETE /api/v1/tasks-gv/<id>/`
- SubTasks (GV):
  - `GET/POST  /api/v1/tasks/subtasks-gv/?task=..&status=..&search=..&ordering=..`
  - `GET/PUT/PATCH/DELETE /api/v1/tasks/subtasks-gv/<id>/`

### HW16 — Category ViewSet + soft-delete
- `GET/POST    /api/v1/tasks/categories/`
- `GET/PATCH/PUT/DELETE /api/v1/tasks/categories/<id>/` — **DELETE** = мягкое удаление.
- Кастом-экшен: `GET /api/v1/tasks/categories/<id>/count_tasks/`

### HW17 — глобальная пагинация + логирование
- **Глобально включена CursorPagination** (6 объектов на страницу) — скрывает `page/limit` в URL.
- Логи:
  - `logs/http_logs.log` — HTTP-запросы (метод, путь, статус).
  - `logs/db_logs.log` — SQL-запросы (INSERT/SELECT/UPDATE) с временем.
  - Логи запуска сервера — в консоль.

### HW18 — JWT + permissions + пагинация 5/стр.

- **Auth**: SimpleJWT (`JWTAuthentication`)  
- **Permissions**: `IsAuthenticated` (по умолчанию)  
- **Pagination**: `CursorPagination`, `page_size = 5`, `ordering = -id`

**JWT эндпоинты:**
- `POST /api/v1/auth/jwt/create/` — `{username, password} → {access, refresh}`
- `POST /api/v1/auth/jwt/refresh/` — `{refresh} → {access}`
- `POST /api/v1/auth/jwt/verify/` — `{token} → 200/401`

**Проверка (Postman):**
- Без токена `GET /api/v1/tasks/` → **401**
- С токеном `GET /api/v1/tasks/` → **200**, есть `next/previous/results`, в `results` ≤ **5**
---

## Быстрая проверка (PyCharm HTTP Client)
Файл `requests.http` в корне содержит все готовые запросы:
- HW12–HW14 (tasks, subtasks, by-day, пагинация)
- HW15 (generic views)
- HW16 (categories + soft-delete + count_tasks)
- HW13-ресабмит: **Categories — create** и второй `POST` с тем же `name` (должен дать **400**).

---

## Стек
- Python 3.11, Django 5.2, DRF
- DRF фильтры/поиск/сортировка (для GV)
- SQLite (по умолчанию)
