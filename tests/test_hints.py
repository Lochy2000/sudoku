from typing import Any

from puzzle.models import PuzzleTemplate
from puzzle.services.gameplay import start_game
from puzzle.services.hints import get_next_hint


def test_hint_returns_first_empty_and_correct_value(db: Any) -> None:
    # Create a trivial template where solution is all 1s and first cell is given '1'
    t = PuzzleTemplate.objects.create(
        size=9,
        box_h=3,
        box_w=3,
        givens=("100" + "0" * 78),
        solution=("1" * 81),
        difficulty_metric=0.2,
        difficulty_label="easy",
        source="test",
    )
    game = start_game(user_id=None, template_id=t.id)

    hint = get_next_hint(game_id=game.id)
    assert hint is not None
    assert hint.cell_index == 1
    assert hint.value == 1
    assert hint.technique == "single-candidate"
