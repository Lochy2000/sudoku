from typing import Any

from puzzle.models import PuzzleTemplate
from puzzle.services.generation import generate_template, map_metric_to_label


def test_map_metric_to_label_ranges() -> None:
    assert map_metric_to_label(0.0) == "easy"
    assert map_metric_to_label(0.25) == "easy"
    assert map_metric_to_label(0.26) == "medium"
    assert map_metric_to_label(0.5) == "medium"
    assert map_metric_to_label(0.51) == "hard"
    assert map_metric_to_label(0.75) == "hard"
    assert map_metric_to_label(0.76) == "expert"


def test_generate_template_creates_row(db: Any) -> None:
    before = PuzzleTemplate.objects.count()
    res = generate_template(size=9, box_h=3, box_w=3, difficulty="medium", seed=123)
    after = PuzzleTemplate.objects.count()
    assert after == before + 1
    t = res.template
    assert len(t.givens) == 81 and len(t.solution) == 81
    assert t.size == 9 and t.box_h == 3 and t.box_w == 3
    assert t.difficulty_label in {"easy", "medium", "hard", "expert"}
