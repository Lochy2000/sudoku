from django.contrib import admin

from .models import DailyChallenge, GameSession, PuzzleTemplate


@admin.register(PuzzleTemplate)
class PuzzleTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "size",
        "box_h",
        "box_w",
        "difficulty_label",
        "source",
        "created_at",
    )
    list_filter = ("size", "difficulty_label", "source", "created_at")
    search_fields = ("source",)
    readonly_fields = ("created_at",)


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "puzzle",
        "status",
        "mistakes_count",
        "time_seconds",
        "started_at",
        "updated_at",
        "completed_at",
    )
    list_filter = ("status", "started_at", "completed_at")
    search_fields = ("user__username",)
    readonly_fields = ("started_at", "updated_at")


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ("date", "puzzle", "created_at")
    list_filter = ("date",)
    search_fields = ("puzzle__source",)
    readonly_fields = ("created_at",)
