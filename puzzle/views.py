from __future__ import annotations

from typing import Any

from django.utils.dateparse import parse_date
from django.conf import settings
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.request import Request
from rest_framework.response import Response

from puzzle.models import DailyChallenge, GameSession, PuzzleTemplate
from puzzle.services.gameplay import start_game, validate_board
from puzzle.services.hints import get_next_hint
from .serializers import GameCreateSerializer, GameUpdateSerializer, PuzzleListQuerySerializer


class PuzzleTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PuzzleTemplate.objects.all()
    http_method_names = ["get"]

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        q = PuzzleListQuerySerializer(data=request.query_params)
        q.is_valid(raise_exception=True)
        size = int(q.validated_data["size"])
        difficulty = str(q.validated_data["difficulty"])
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
    # In strict mode, only authenticated users can create/update/fetch games.
    # Otherwise AllowAny for MVP convenience.
    def get_permissions(self) -> list[permissions.BasePermission]:  # type: ignore[override]
        if settings.SECURITY_STRICT_API:
            if self.action in {"create", "update", "check", "hint", "retrieve"}:
                return [permissions.IsAuthenticated()]  # type: ignore[list-item]
        return [permissions.AllowAny()]  # type: ignore[list-item]

    def create(self, request: Request) -> Response:
        ser = GameCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        template_id = int(ser.validated_data["template_id"])  # raises KeyError if missing
        user_id = request.user.id if request.user.is_authenticated else None
        game = start_game(user_id=user_id, template_id=template_id)
        return Response({"id": game.id, "status": game.status, "board_state": game.board_state})

    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        assert pk is not None
        game = GameSession.objects.get(pk=int(pk))
        if settings.SECURITY_STRICT_API:
            # Enforce ownership when strict
            if game.user_id is not None:
                if not request.user.is_authenticated or request.user.id != game.user_id:
                    return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
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
        game = GameSession.objects.select_related("puzzle").get(pk=int(pk))
        if settings.SECURITY_STRICT_API:
            if game.user_id is not None:
                if not request.user.is_authenticated or request.user.id != game.user_id:
                    return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        ser = GameUpdateSerializer(data=request.data, partial=True, context={"size": game.puzzle.size})
        ser.is_valid(raise_exception=True)

        data = ser.validated_data
        update_fields: list[str] = []
        if "board_state" in data:
            game.board_state = data["board_state"]
            update_fields.append("board_state")
        if "pencil_marks" in data:
            game.pencil_marks = data["pencil_marks"]
            update_fields.append("pencil_marks")
        if "time_seconds" in data:
            game.time_seconds = int(data["time_seconds"])  # still trusting client time
            update_fields.append("time_seconds")
        if update_fields:
            update_fields.append("updated_at")
            game.save(update_fields=update_fields)
        return Response({"ok": True})

    @action(detail=True, methods=["post"], url_path="check")
    def check(self, request: Request, pk: str | None = None) -> Response:
        assert pk is not None
        ok = validate_board(game_id=int(pk))
        return Response({"solved": ok})

    @action(detail=True, methods=["post"], url_path="hint")
    def hint(self, request: Request, pk: str | None = None) -> Response:
        assert pk is not None
        hint = get_next_hint(game_id=int(pk))
        if hint is None:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response(
            {
                "cell_index": hint.cell_index,
                "value": hint.value,
                "technique": hint.technique,
            }
        )


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
