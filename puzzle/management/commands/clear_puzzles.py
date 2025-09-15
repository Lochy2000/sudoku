from __future__ import annotations

import os
from typing import Any

from django.core.management.base import BaseCommand

from puzzle.models import PuzzleTemplate


class Command(BaseCommand):
    help = "Delete all PuzzleTemplate rows (disabled in prod)."

    def handle(self, *args: Any, **options: Any) -> None:
        if os.getenv("DJANGO_ENV", "dev") == "prod":
            self.stderr.write(self.style.ERROR("Refusing to clear puzzles in prod"))
            return

        count, _ = PuzzleTemplate.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"Deleted {count} templates"))
