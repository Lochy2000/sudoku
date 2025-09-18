from __future__ import annotations

from typing import Any

from django.utils.dateparse import parse_date
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.request import Request
from rest_framework.response import Response

from puzzle.models import DailyChallenge, GameSession, PuzzleTemplate
from puzzle.services.gameplay import start_game, validate_board


class PuzzleTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PuzzleTemplate.objects.all()
    http_method_names = ["get"]

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        size = int(request.query_params.get("size", 9))
        difficulty = request.query_params.get("difficulty", "medium")
        obj = (
            PuzzleTemplate.objects.filter(size=size, difficulty_label=difficulty)
            .order_by("?")
            .first()
        )
        if obj is None:
            return Response({"detail": "No puzzle available"}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                "id": obj.id,
                "size": obj.size,
                "box_h": obj.box_h,
                "box_w": obj.box_w,
                "givens": obj.givens,
                "difficulty": obj.difficulty_label,
            }
        )


class GameSessionViewSet(viewsets.ViewSet):
    http_method_names = ["get", "post", "put"]

    def create(self, request: Request) -> Response:
        template_id = int(request.data["template_id"])  # raises KeyError if missing
        user_id = request.user.id if request.user.is_authenticated else None
        game = start_game(user_id=user_id, template_id=template_id)
        return Response({"id": game.id, "status": game.status, "board_state": game.board_state})

    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        assert pk is not None
        game = GameSession.objects.get(pk=int(pk))
        return Response(
            {
                "id": game.id,
                "status": game.status,
                "board_state": game.board_state,
                "pencil_marks": game.pencil_marks,
                "puzzle_id": game.puzzle_id,
            }
        )

    def update(self, request: Request, pk: str | None = None) -> Response:
        assert pk is not None
        game = GameSession.objects.get(pk=int(pk))
        fields = {}
        if "board_state" in request.data:
            fields["board_state"] = request.data["board_state"]
        if "pencil_marks" in request.data:
            fields["pencil_marks"] = request.data["pencil_marks"]
        if "time_seconds" in request.data:
            fields["time_seconds"] = int(request.data["time_seconds"])  # trust client for MVP
        for k, v in fields.items():
            setattr(game, k, v)
        if fields:
            game.save(update_fields=[*fields.keys(), "updated_at"])
        return Response({"ok": True})

    @action(detail=True, methods=["post"], url_path="check")
    def check(self, request: Request, pk: str | None = None) -> Response:
        assert pk is not None
        ok = validate_board(game_id=int(pk))
        return Response({"solved": ok})


@api_view(["GET"])
def daily_challenge_view(request: Request, date: str) -> Response:
    dt = parse_date(date)
    if dt is None:
        return Response({"detail": "Invalid date"}, status=status.HTTP_400_BAD_REQUEST)
    dc = DailyChallenge.objects.filter(date=dt).select_related("puzzle").first()
    if dc is None:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    p = dc.puzzle
    return Response(
        {
            "date": str(dc.date),
            "puzzle": {
                "id": p.id,
                "size": p.size,
                "box_h": p.box_h,
                "box_w": p.box_w,
                "givens": p.givens,
                "difficulty": p.difficulty_label,
            },
        }
    )
