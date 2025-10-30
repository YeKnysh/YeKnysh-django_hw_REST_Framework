# tasks/pagination.py
from rest_framework.pagination import CursorPagination

class DefaultCursorPagination(CursorPagination):
    page_size = 5          # 5 элементов на страницу
    ordering = '-id'       # стабильно, по убыванию id
