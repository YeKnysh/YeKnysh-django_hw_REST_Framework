# HW12–HW14 — Task Manager API (DRF)

## Запуск
1) python -m venv venv && venv\Scripts\activate   # Windows
2) pip install -r requirements.txt
3) python manage.py migrate
4) python manage.py runserver

## HW12 — базовые эндпоинты
- POST /api/v1/tasks/create/ — создание задачи (title, description, status[new|in_progress|done], deadline YYYY-MM-DD)
- GET  /api/v1/tasks/        — список задач
- GET  /api/v1/tasks/<id>/   — детальная задача
- GET  /api/v1/tasks/stats/  — статистика (total, by_status, overdue)
- GET  /api/ping/            — технический пинг (DRF UI)

## HW13 — сериализаторы и представления
Модели: `Category`, `SubTask` (+ у `Task` поле `category`).
- Вложенность: в `TaskDetail` добавлен массив `subtasks`.
- Валидация: deadline не может быть в прошлом.
- Category: проверка уникальности имени.
- SubTask API (APIView):
  - GET/POST  /api/v1/tasks/subtasks/
  - GET/PUT/PATCH/DELETE /api/v1/tasks/subtasks/<id>/

## HW14 — query params и пагинация
- GET /api/v1/tasks/by-day/?day=<понедельник|вторник|...|monday|tuesday|...>  
  Без параметра — вернуть все задачи. День берётся из `deadline`.
- GET /api/v1/tasks/subtasks/?page=1&task=<id>&task_title=<str>&status=<new|in_progress|done>  
  Пагинация: 5 на страницу, сортировка — по `created_at` убыванию. Фильтры опциональны.

## Быстрая проверка (PyCharm HTTP Client)
Смотри файл `requests.http` в корне репозитория (в нём все запросы для HW12–HW14).

## HW15 — Generic Views
- Tasks (GV): 
  - GET/POST  /api/v1/tasks-gv/  (?search=..&status=..&ordering=.., пагинация по 5)
  - GET/PUT/PATCH/DELETE /api/v1/tasks-gv/<id>/
- SubTasks (GV):
  - GET/POST  /api/v1/tasks/subtasks-gv/  (?task=..&status=..&search=..&ordering=.., пагинация)
  - GET/PUT/PATCH/DELETE /api/v1/tasks/subtasks-gv/<id>/
Используются Search/Ordering/DjangoFilter backends.
