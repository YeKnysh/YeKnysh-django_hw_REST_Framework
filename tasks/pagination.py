# tasks/pagination.py
from rest_framework.pagination import CursorPagination

class DefaultCursorPagination(CursorPagination):
    page_size = 6          # по заданию: не более 6 объектов на странице
    ordering = '-id'       # стабильно и безопасно (движение по убыванию id)
