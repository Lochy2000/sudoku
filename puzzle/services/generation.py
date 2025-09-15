from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction

from puzzle.models import PuzzleTemplate
from puzzle.services.engines import GridSpec
from puzzle.services.factory import get_engine_for


@dataclass(frozen=True)
class GenerationResult:
    template: PuzzleTemplate


def map_metric_to_label(metric: float) -> str:
    """Simple mapping; later make configurable.
    0.0..0.25 -> easy, 0.25..0.5 -> medium, 0.5..0.75 -> hard, else expert
    """
    if metric <= 0.25:
        return PuzzleTemplate.DIFFICULTY_EASY
    if metric <= 0.5:
        return PuzzleTemplate.DIFFICULTY_MEDIUM
    if metric <= 0.75:
        return PuzzleTemplate.DIFFICULTY_HARD
    return PuzzleTemplate.DIFFICULTY_EXPERT


@transaction.atomic
def generate_template(
    *,
    size: int,
    box_h: int,
    box_w: int,
    difficulty: str,
    source: str | None = None,
    seed: int | None = None,
) -> GenerationResult:
    spec = GridSpec(size=size, box_h=box_h, box_w=box_w)
    engine = get_engine_for(spec, source=None)
    givens, solution, metric = engine.generate(spec=spec, difficulty=difficulty, seed=seed)

    # Validate uniqueness before saving
    if not engine.has_unique_solution(spec=spec, grid=givens):
        raise ValueError("Generated puzzle is not uniquely solvable")

    label = map_metric_to_label(metric)
    template = PuzzleTemplate.objects.create(
        size=size,
        box_h=box_h,
        box_w=box_w,
        givens=givens,
        solution=solution,
        difficulty_metric=metric,
        difficulty_label=label,
        source=source or "engine",
    )
    return GenerationResult(template=template)
