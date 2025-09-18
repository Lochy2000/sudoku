import datetime as dt
from typing import Any

from django.core.management import call_command

from puzzle.models import DailyChallenge, PuzzleTemplate
from puzzle.services.daily import create_daily_challenge


def test_create_daily_idempotent(db: Any) -> None:
    PuzzleTemplate.objects.create(
        size=9,
        box_h=3,
        box_w=3,
        givens=("0" * 81),
        solution=("1" * 81),
        difficulty_metric=0.3,
        difficulty_label="easy",
        source="test",
    )
    day = dt.date(2025, 9, 17)

    res1 = create_daily_challenge(date=day, size=9, difficulty="easy")
    assert res1.created is True
    res2 = create_daily_challenge(date=day, size=9, difficulty="easy")
    assert res2.created is False
    assert res1.challenge.id == res2.challenge.id


def test_seed_daily_command(db: Any) -> None:
    # ensure at least one template exists
    if PuzzleTemplate.objects.count() == 0:
        PuzzleTemplate.objects.create(
            size=9,
            box_h=3,
            box_w=3,
            givens=("0" * 81),
            solution=("1" * 81),
            difficulty_metric=0.4,
            difficulty_label="medium",
            source="test",
        )

    call_command(
        "seed_daily",
        "--start",
        "2025-09-15",
        "--days",
        "3",
        "--size",
        "9",
        "--difficulty",
        "medium",
    )
    assert DailyChallenge.objects.filter(date__range=("2025-09-15", "2025-09-17")).count() == 3
