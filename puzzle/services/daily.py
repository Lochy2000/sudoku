from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from django.db import transaction

from puzzle.models import DailyChallenge, PuzzleTemplate


@dataclass(frozen=True)
class DailyResult:
    challenge: DailyChallenge
    created: bool


@transaction.atomic
def create_daily_challenge(
    *, date: dt.date, size: int = 9, difficulty: str = "medium"
) -> DailyResult:
    existing = DailyChallenge.objects.select_related("puzzle").filter(date=date).first()
    if existing is not None:
        return DailyResult(challenge=existing, created=False)

    template = (
        PuzzleTemplate.objects.filter(size=size, difficulty_label=difficulty).order_by("?").first()
    )
    if template is None:
        raise ValueError("No PuzzleTemplate available for requested size/difficulty")

    dc = DailyChallenge.objects.create(date=date, puzzle=template)
    return DailyResult(challenge=dc, created=True)
