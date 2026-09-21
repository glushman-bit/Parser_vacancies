"""
URL configuration for config project.

Взаимодействие с пользователем реализовано:
- через HTML-шаблоны (страницы отчётов и действий);
- через REST API (Django REST Framework) по префиксу /api/.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("hh_parser.urls")),
    path("api/", include("hh_parser.api_urls")),
]
