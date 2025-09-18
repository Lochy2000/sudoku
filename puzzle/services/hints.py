from __future__ import annotations

from dataclasses import dataclass

from puzzle.models import GameSession


@dataclass(frozen=True)
class Hint:
    cell_index: int
    value: int
    technique: str


def get_next_hint(*, game_id: int) -> Hint | None:
    """
    Very simple hint strategy for MVP:
    - Find the first empty cell '0' in the current board_state
    - Suggest the correct value from the template solution
    - Report technique as 'single-candidate' (placeholder)
    Returns None if no empty cells remain.
    """
    game = GameSession.objects.select_related("puzzle").get(pk=game_id)
    if not isinstance(game.board_state, str):
        # Only support string board_state in MVP hints
        return None

    board = game.board_state
    try:
        idx = board.index("0")
    except ValueError:
        return None

    correct_char = game.puzzle.solution[idx]
    try:
        correct_value = int(correct_char)
    except ValueError:
        return None

    return Hint(cell_index=idx, value=correct_value, technique="single-candidate")
