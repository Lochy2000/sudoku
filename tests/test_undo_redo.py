from typing import Any

import pytest

from puzzle.models import GameSession, PuzzleTemplate
from puzzle.services.gameplay import apply_move, start_game


def test_illegal_edit_given_raises_error(db: Any) -> None:
    t = PuzzleTemplate.objects.create(
        size=9,
        box_h=3,
        box_w=3,
        givens=("1" + "0" * 80),
        solution=("1" * 81),
        difficulty_metric=0.2,
        difficulty_label="easy",
        source="test",
    )
    game = start_game(user_id=None, template_id=t.id)

    with pytest.raises(ValueError):
        apply_move(game_id=game.id, cell_index=0, value=2, mode="number")


def test_legality_and_mistake_tracking_mvp(db: Any) -> None:
    t = PuzzleTemplate.objects.create(
        size=9,
        box_h=3,
        box_w=3,
        givens=("0" * 81),
        solution=("1" * 81),
        difficulty_metric=0.2,
        difficulty_label="easy",
        source="test",
    )
    game = start_game(user_id=None, template_id=t.id)

    # Place correct value, then overwrite with 0 (simulate undo via client)
    apply_move(game_id=game.id, cell_index=5, value=1, mode="number")
    apply_move(game_id=game.id, cell_index=5, value=0, mode="number")
    g = GameSession.objects.get(pk=game.id)
    assert g.board_state[5] == "0"
