# HW12–16 — Task Manager API (DRF)

## Запуск
1) `python -m venv venv && venv\Scripts\activate`  *(Windows)*
2) `pip install -r requirements.txt`
3) `python manage.py migrate`
4) `python manage.py runserver`

## Что есть
- **HW12** — FBV по задачам:
  - `POST /api/v1/tasks/create/`
  - `GET  /api/v1/tasks/`
  - `GET  /api/v1/tasks/<id>/`
  - `GET  /api/v1/tasks/stats/`
- **HW13** — SubTask (APIView) + вложенные subtasks в деталке Task.
- **HW14** — фильтр задач по дню недели `GET /api/v1/tasks/by-day/?day=...`, пагинация/фильтры SubTask.
- **HW15** — Generic Views (параллельно старым):
  - `GET/POST /api/v1/tasks-gv/`
  - `GET/PUT/PATCH/DELETE /api/v1/tasks-gv/<id>/`
  - `GET/POST /api/v1/tasks/subtasks-gv/`
  - `GET/PUT/PATCH/DELETE /api/v1/tasks/subtasks-gv/<id>/`
- **HW16** — Categories через **ModelViewSet** + soft-delete:
  - `GET/POST /api/v1/tasks/categories/`
  - `GET/PATCH/PUT/DELETE /api/v1/tasks/categories/<id>/` *(DELETE = мягкое удаление)*
  - `GET /api/v1/tasks/categories/<id>/count_tasks/` *(кастомный action)*
  - `POST /api/v1/tasks/categories/<id>/restore/` *(восстановление мягко удалённой)*

## Быстрая проверка
Смотри `requests.http` — все сценарии (создание/списки/детали/поиск/сортировка/soft-delete/restore/count).
