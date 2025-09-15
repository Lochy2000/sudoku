from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from puzzle.services.generation import generate_template


class Command(BaseCommand):
    help = "Generate and store a number of PuzzleTemplate rows"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--size", type=int, default=9)
        parser.add_argument("--box-h", type=int, default=3)
        parser.add_argument("--box-w", type=int, default=3)
        parser.add_argument("--difficulty", type=str, default="medium")
        parser.add_argument("--count", type=int, default=10)
        parser.add_argument("--source", type=str, default="dokusan")
        parser.add_argument("--seed", type=int, default=None)

    def handle(self, *args: Any, **options: Any) -> None:
        size = int(options["size"])  # typed narrowing
        box_h = int(options["box_h"])  # typed narrowing
        box_w = int(options["box_w"])  # typed narrowing
        difficulty = str(options["difficulty"])  # typed narrowing
        count = int(options["count"])  # typed narrowing
        source = str(options["source"])  # typed narrowing
        seed = options.get("seed")

        created = 0
        for i in range(count):
            # vary seed slightly for reproducibility across multiple rows
            s = None if seed is None else seed + i
            res = generate_template(
                size=size,
                box_h=box_h,
                box_w=box_w,
                difficulty=difficulty,
                source=source,
                seed=s,
            )
            created += 1
            self.stdout.write(self.style.SUCCESS(f"Created template #{res.template.id}"))

        self.stdout.write(self.style.SUCCESS(f"Done. Created: {created}"))
