"""
URL configuration for sudoku_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.urls import URLPattern, URLResolver, include, path
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from puzzle.views import GameSessionViewSet, PuzzleTemplateViewSet, daily_challenge_view


def healthcheck(_request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")


router = DefaultRouter()
router.register(r"puzzles", PuzzleTemplateViewSet, basename="puzzles")
router.register(r"games", GameSessionViewSet, basename="games")


urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path("healthz", healthcheck),
    path("accounts/", include("accounts.urls")),
    path("api/", include(router.urls)),
    path("api/daily/<date>", daily_challenge_view),
    path(
        "api/schema",
        get_schema_view(
            title="Sudoku API",
            description="API schema for Sudoku backend",
            version="1.0.0",
        ),
        name="openapi-schema",
    ),
]
