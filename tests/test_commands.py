import io
from typing import Any

from django.core.management import call_command

from puzzle.models import PuzzleTemplate


def test_seed_and_clear_commands(db: Any) -> None:
    out = io.StringIO()
    call_command(
        "seed_puzzles",
        "--size",
        "9",
        "--box-h",
        "3",
        "--box-w",
        "3",
        "--difficulty",
        "medium",
        "--count",
        "2",
        stdout=out,
    )
    assert PuzzleTemplate.objects.count() >= 2

    out = io.StringIO()
    call_command("clear_puzzles", stdout=out)
    assert PuzzleTemplate.objects.count() == 0
