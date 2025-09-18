from __future__ import annotations

# mypy: ignore-errors
import json
from typing import Any

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.urls import path

from .models import AnalyticsEvent, DailyChallenge, GameSession, PuzzleTemplate
from .services.analytics import average_time_seconds_by_difficulty
from .services.engines import GridSpec
from .services.factory import get_engine_for


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
    actions = ("validate_templates", "export_selected_json")

    def validate_templates(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Validate selected templates for uniqueness using the engine."""
        total = 0
        invalid = 0
        for t in queryset:  # type: ignore[assignment]
            total += 1
            spec = GridSpec(size=t.size, box_h=t.box_h, box_w=t.box_w)
            engine = get_engine_for(spec)
            if not engine.has_unique_solution(spec=spec, grid=t.givens):
                invalid += 1
        if invalid == 0:
            self.message_user(
                request, f"Validated {total} template(s): all OK", level=messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                f"Validated {total} template(s): {invalid} invalid",
                level=messages.ERROR,
            )

    validate_templates.short_description = "Validate uniqueness for selected templates"  # type: ignore[attr-defined]

    def export_selected_json(self, request: HttpRequest, queryset: QuerySet) -> HttpResponse:
        """Export selected templates as a JSON array download."""
        items = []
        for t in queryset:  # type: ignore[assignment]
            items.append(
                {
                    "id": t.id,
                    "size": t.size,
                    "box_h": t.box_h,
                    "box_w": t.box_w,
                    "givens": t.givens,
                    "solution": t.solution,
                    "difficulty_metric": t.difficulty_metric,
                    "difficulty_label": t.difficulty_label,
                    "source": t.source,
                    "created_at": t.created_at.isoformat(),
                }
            )
        data = json.dumps(items)
        resp = HttpResponse(data, content_type="application/json")
        resp["Content-Disposition"] = "attachment; filename=puzzles.json"
        return resp

    export_selected_json.short_description = "Export selected templates as JSON"  # type: ignore[attr-defined]

    def get_urls(self) -> list:  # type: ignore[override]
        urls = super().get_urls()
        custom = [
            path(
                "queue/",
                self.admin_site.admin_view(self.queue_view),
                name="puzzle_puzzletemplate_queue",
            ),
        ]
        return custom + urls

    def queue_view(self, request: HttpRequest) -> HttpResponse:
        if request.method == "POST":
            # Handle JSON import
            json_text = request.POST.get("json", "").strip()
            if json_text:
                try:
                    payload = json.loads(json_text)
                    if not isinstance(payload, list):
                        raise ValueError("Expected a JSON array")
                    created = 0
                    for item in payload:
                        PuzzleTemplate.objects.create(
                            size=int(item["size"]),
                            box_h=int(item["box_h"]),
                            box_w=int(item["box_w"]),
                            givens=str(item["givens"]),
                            solution=str(item["solution"]),
                            difficulty_metric=float(item.get("difficulty_metric", 0.0)),
                            difficulty_label=str(
                                item.get("difficulty_label", PuzzleTemplate.DIFFICULTY_EASY)
                            ),
                            source=str(item.get("source", "import")),
                        )
                        created += 1
                    self.message_user(
                        request, f"Imported {created} puzzle(s)", level=messages.SUCCESS
                    )
                except Exception as exc:  # pragma: no cover - edge case messaging
                    self.message_user(request, f"Import failed: {exc}", level=messages.ERROR)
            return redirect("admin:puzzle_puzzletemplate_queue")

        # Compute queue depth summary
        from django.db.models import Count

        # Build queryset in steps with Any casts to avoid mypy internal error
        base: Any = PuzzleTemplate.objects.values("size", "difficulty_label")
        ordered: Any = base.order_by("size", "difficulty_label")
        summary = ordered.annotate(count=Count("id"))
        rows = [
            f"<tr><td>{s['size']}</td><td>{s['difficulty_label']}</td><td>{s['count']}</td></tr>"
            for s in summary
        ]
        table = "".join(rows) or "<tr><td colspan='3'>No data</td></tr>"
        token = get_token(request)
        html = f"""
            <div class='container'>
              <h1>Puzzle Queue</h1>
              <p>Counts by size and difficulty.</p>
              <table class='adminlist'>
                <thead><tr><th>Size</th><th>Difficulty</th><th>Count</th></tr></thead>
                <tbody>{table}</tbody>
              </table>
              <h2>Import JSON</h2>
              <form method='post'>
                <input type='hidden' name='csrfmiddlewaretoken' value='{token}' />
                <textarea name='json' rows='8' cols='80' placeholder='[ ... ]'></textarea><br/>
                <button type='submit' class='default'>Import</button>
              </form>
            </div>
        """
        return HttpResponse(html)


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

    def get_urls(self) -> list:  # type: ignore[override]
        urls = super().get_urls()
        custom = [
            path(
                "analytics/",
                self.admin_site.admin_view(self.analytics_view),
                name="puzzle_gamesession_analytics",
            ),
        ]
        return custom + urls

    def analytics_view(self, request: HttpRequest) -> HttpResponse:
        size_param = request.GET.get("size")
        size = int(size_param) if size_param and size_param.isdigit() else None
        rows = average_time_seconds_by_difficulty(size=size)
        tr = (
            "".join(
                f"<tr><td>{r.difficulty_label}</td><td>{r.average_time_seconds:.1f}</td></tr>"
                for r in rows
            )
            or "<tr><td colspan='2'>No data</td></tr>"
        )
        html = f"""
            <div class='container'>
              <h1>Analytics — Average Completion Time</h1>
              <form method='get' style='margin-bottom:1rem'>
                <label>Size:
                  <input type='number' name='size' value='{size or ''}' placeholder='(any)'
                         min='1'/>
                </label>
                <button type='submit' class='default'>Filter</button>
              </form>
              <table class='adminlist'>
                <thead><tr><th>Difficulty</th><th>Avg Time (s)</th></tr></thead>
                <tbody>{tr}</tbody>
              </table>
            </div>
        """
        return HttpResponse(html)


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ("date", "puzzle", "created_at")
    list_filter = ("date",)
    search_fields = ("puzzle__source",)
    readonly_fields = ("created_at",)


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "game", "created_at")
    list_filter = ("name", "created_at")
    search_fields = ("name", "user__username")
    readonly_fields = ("created_at",)
