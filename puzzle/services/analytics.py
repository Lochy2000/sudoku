from __future__ import annotations

from dataclasses import dataclass

from django.db.models import Avg, QuerySet

from puzzle.models import GameSession


@dataclass(frozen=True)
class AverageTimeByDifficulty:
    difficulty_label: str
    average_time_seconds: float


def average_time_seconds_by_difficulty(*, size: int | None = None) -> list[AverageTimeByDifficulty]:
    """Return average completion time per difficulty label for completed games.

    Optionally filter by puzzle size.
    """
    qs: QuerySet[GameSession] = GameSession.objects.select_related("puzzle").filter(
        status=GameSession.STATUS_COMPLETED
    )
    if size is not None:
        qs = qs.filter(puzzle__size=size)

    rows = (
        qs.values("puzzle__difficulty_label")
        .order_by("puzzle__difficulty_label")
        .annotate(avg_time=Avg("time_seconds"))
    )
    return [
        AverageTimeByDifficulty(
            difficulty_label=r["puzzle__difficulty_label"],
            average_time_seconds=float(r["avg_time"]) if r["avg_time"] is not None else 0.0,
        )
        for r in rows
    ]
