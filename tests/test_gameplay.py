from typing import Any

import pytest

from puzzle.models import GameSession, PuzzleTemplate
from puzzle.services.gameplay import (
    apply_move,
    complete_game,
    start_game,
    validate_board,
)


@pytest.fixture
def template(db: Any) -> PuzzleTemplate:
    return PuzzleTemplate.objects.create(
        size=9,
        box_h=3,
        box_w=3,
        givens=("100" + "0" * 78),  # cell 0 is a given '1'
        solution=("1" * 81),
        difficulty_metric=0.5,
        difficulty_label="medium",
        source="test",
    )


def test_start_apply_validate_complete(db: Any, template: PuzzleTemplate) -> None:
    game = start_game(user_id=None, template_id=template.id)
    assert isinstance(game, GameSession)
    assert game.board_state == template.givens

    # Attempt to edit a given should error
    with pytest.raises(ValueError):
        apply_move(game_id=game.id, cell_index=0, value=9, mode="number")

    # Fill a non-given cell
    res = apply_move(game_id=game.id, cell_index=1, value=1, mode="number")
    assert res.game.board_state[1] == "1"

    # Toggle pencil marks
    res = apply_move(game_id=game.id, cell_index=2, value=3, mode="pencil")
    assert res.game.pencil_marks.get("2") == [3]
    res = apply_move(game_id=game.id, cell_index=2, value=3, mode="pencil")
    assert "2" not in res.game.pencil_marks

    # Not solved yet
    assert validate_board(game_id=game.id) is False

    # Force solve by setting board_state to solution and validate
    game.board_state = template.solution
    game.save(update_fields=["board_state"])
    assert validate_board(game_id=game.id) is True

    # Complete
    game = complete_game(game_id=game.id)
    assert game.status == GameSession.STATUS_COMPLETED
    assert game.completed_at is not None
