from __future__ import annotations

import datetime as dt

from celery import shared_task
from django.db.models import Count

from puzzle.models import PuzzleTemplate
from puzzle.services.daily import create_daily_challenge
from puzzle.services.generation import generate_template


@shared_task
def refill_puzzle_queue(*, size: int = 9, difficulty: str = "medium", min_count: int = 20) -> int:
    """Ensure there are at least `min_count` templates for size/difficulty.

    Returns the number of templates created.
    """
    existing = (
        PuzzleTemplate.objects.filter(size=size, difficulty_label=difficulty)
        .aggregate(c=Count("id"))
        .get("c", 0)
    )
    created = 0
    while existing + created < min_count:
        generate_template(size=size, box_h=3, box_w=3, difficulty=difficulty)
        created += 1
    return created


@shared_task
def precreate_daily_challenges(
    *, days_ahead: int = 7, size: int = 9, difficulty: str = "medium"
) -> int:
    """Create DailyChallenge rows for the next N days if missing.

    Returns the number of new daily challenges created.
    """
    today = dt.date.today()
    created = 0
    for i in range(days_ahead):
        target = today + dt.timedelta(days=i)
        res = create_daily_challenge(date=target, size=size, difficulty=difficulty)
        if res.created:
            created += 1
    return created
