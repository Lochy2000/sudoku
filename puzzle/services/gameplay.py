from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.utils import timezone

from puzzle.models import AnalyticsEvent, GameSession, PuzzleTemplate


@dataclass(frozen=True)
class MoveResult:
    game: GameSession


def _index_bounds_check(index: int, size: int) -> None:
    total = size * size
    if index < 0 or index >= total:
        raise ValueError(f"cell_index out of range 0..{total-1}")


def start_game(*, user_id: int | None, template_id: int) -> GameSession:
    template = PuzzleTemplate.objects.get(pk=template_id)
    board_state = template.givens
    game = GameSession.objects.create(
        user_id=user_id,
        puzzle=template,
        board_state=board_state,
        pencil_marks={},
        mistakes_count=0,
        time_seconds=0,
    )
    # Analytics: game start
    AnalyticsEvent.objects.create(
        name=AnalyticsEvent.EVENT_GAME_START,
        user_id=user_id,
        game=game,
        payload={"template_id": template.id},
    )
    return game


def apply_move(
    *,
    game_id: int,
    cell_index: int,
    value: int,
    mode: str = "number",
) -> MoveResult:
    game = GameSession.objects.select_related("puzzle").get(pk=game_id)
    size = game.puzzle.size
    _index_bounds_check(cell_index, size)
    if not (0 <= value <= size):
        raise ValueError("value out of range")

    # Disallow editing givens
    if game.puzzle.givens[cell_index] != "0":
        raise ValueError("Cannot change a given cell")

    # Ensure board_state is a string; if JSON structure, normalize by joining
    if isinstance(game.board_state, str):
        board = list(game.board_state)
    elif isinstance(game.board_state, list):
        board = [str(v) for v in game.board_state]
    else:
        # Attempt to coerce common JSON-like structures
        if isinstance(game.board_state, dict) and "board" in game.board_state:
            raw: Any = game.board_state["board"]
            if isinstance(raw, str):
                board = list(raw)
            elif isinstance(raw, list):
                board = [str(v) for v in raw]
            else:
                raise ValueError("Unsupported board_state format")
        else:
            raise ValueError("Unsupported board_state format")

    if mode == "number":
        board[cell_index] = "0" if value == 0 else str(value)
    elif mode == "pencil":
        marks: dict[str, list[int]] = game.pencil_marks or {}
        key = str(cell_index)
        current = set(marks.get(key, []))
        if value == 0:
            current.clear()
        else:
            if value in current:
                current.remove(value)
            else:
                current.add(value)
        if current:
            marks[key] = sorted(current)
        elif key in marks:
            del marks[key]
        game.pencil_marks = marks
    else:
        raise ValueError("Unknown mode; expected 'number' or 'pencil'")

    # Persist board back as string
    game.board_state = "".join(board)
    game.save(update_fields=["board_state", "pencil_marks", "updated_at"])
    return MoveResult(game=game)


def validate_board(*, game_id: int) -> bool:
    game = GameSession.objects.select_related("puzzle").get(pk=game_id)
    if not isinstance(game.board_state, str):
        return False
    return game.board_state == game.puzzle.solution


def complete_game(*, game_id: int) -> GameSession:
    game = GameSession.objects.get(pk=game_id)
    game.status = GameSession.STATUS_COMPLETED
    game.completed_at = timezone.now()
    game.save(update_fields=["status", "completed_at", "updated_at"])
    # Analytics: game complete
    AnalyticsEvent.objects.create(
        name=AnalyticsEvent.EVENT_GAME_COMPLETE,
        user=game.user,
        game=game,
        payload={"time_seconds": game.time_seconds, "mistakes": game.mistakes_count},
    )
    return game
