from __future__ import annotations

import datetime as dt
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from puzzle.services.daily import create_daily_challenge


class Command(BaseCommand):
    help = "Seed DailyChallenge rows for a date range"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--start", type=str, required=True, help="YYYY-MM-DD start date")
        parser.add_argument("--days", type=int, default=7)
        parser.add_argument("--size", type=int, default=9)
        parser.add_argument("--difficulty", type=str, default="medium")

    def handle(self, *args: Any, **options: Any) -> None:
        start = dt.date.fromisoformat(options["start"])  # raises if invalid
        days = int(options["days"])  # typed narrowing
        size = int(options["size"])  # typed narrowing
        difficulty = str(options["difficulty"])  # typed narrowing

        created = 0
        for i in range(days):
            d = start + dt.timedelta(days=i)
            res = create_daily_challenge(date=d, size=size, difficulty=difficulty)
            if res.created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created daily for {d}"))
            else:
                self.stdout.write(self.style.WARNING(f"Exists for {d}: {res.challenge.puzzle_id}"))

        self.stdout.write(self.style.SUCCESS(f"Done. Created {created} of {days}"))
