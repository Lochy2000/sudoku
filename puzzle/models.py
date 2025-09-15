from __future__ import annotations

from django.conf import settings
from django.db import models


class PuzzleTemplate(models.Model):
    """
    Canonical, reusable Sudoku puzzle definition.

    Serialization formats:
    - givens: 1D string of length size*size using "0" for empty cells.
    - solution: 1D string of length size*size with digits/values 1..size.
    Grid geometry is defined by size and sub-box dimensions box_h × box_w.
    """

    DIFFICULTY_EASY = "easy"
    DIFFICULTY_MEDIUM = "medium"
    DIFFICULTY_HARD = "hard"
    DIFFICULTY_EXPERT = "expert"
    DIFFICULTY_CHOICES = [
        (DIFFICULTY_EASY, "Easy"),
        (DIFFICULTY_MEDIUM, "Medium"),
        (DIFFICULTY_HARD, "Hard"),
        (DIFFICULTY_EXPERT, "Expert"),
    ]

    size = models.PositiveSmallIntegerField(help_text="Number of rows/cols (e.g., 9)")
    box_h = models.PositiveSmallIntegerField(help_text="Sub-box height (e.g., 3 for 9×9)")
    box_w = models.PositiveSmallIntegerField(help_text="Sub-box width (e.g., 3 for 9×9)")

    givens = models.TextField(
        help_text=("Board string of length size*size, '0' for empty. Indexing is row-major.")
    )
    solution = models.TextField(
        help_text=("Solved board string of length size*size, values 1..size in row-major order.")
    )

    difficulty_metric = models.FloatField(
        help_text="Raw engine metric used to derive difficulty label"
    )
    difficulty_label = models.CharField(
        max_length=16, choices=DIFFICULTY_CHOICES, help_text="Bucketed difficulty label"
    )
    source = models.CharField(
        max_length=64, help_text="Origin of puzzle (e.g., engine name or import source)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["size", "difficulty_label"], name="puzzle_size_diff"),
        ]
        ordering = ["-created_at", "size", "difficulty_label"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"PuzzleTemplate(id={self.pk}, size={self.size}, diff={self.difficulty_label})"


class GameSession(models.Model):
    """
    A single player's play-through state for a given `PuzzleTemplate`.

    Serialization formats:
    - board_state: 1D string or JSON payload that encodes the current board.
      If a string, length is size*size with '0' for empty.
    - pencil_marks: JSON object mapping cell_index -> list[int].
    """

    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_ABANDONED = "abandoned"
    STATUS_CHOICES = [
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_ABANDONED, "Abandoned"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    puzzle = models.ForeignKey(PuzzleTemplate, on_delete=models.PROTECT)

    board_state = models.JSONField(
        default=str,
        help_text=(
            "Current board; either 1D string or structured JSON. Use '0' for empty if string."
        ),
    )
    pencil_marks = models.JSONField(
        default=dict,
        help_text="Map of cell_index (0..N-1) to list of candidate integers",
    )

    mistakes_count = models.PositiveIntegerField(default=0)
    time_seconds = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_IN_PROGRESS)

    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return (
            f"GameSession(id={self.pk}, user={self.user_id}, "
            f"puzzle={self.puzzle_id}, status={self.status})"
        )


class DailyChallenge(models.Model):
    """One featured puzzle per calendar date."""

    date = models.DateField(unique=True)
    puzzle = models.ForeignKey(PuzzleTemplate, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"DailyChallenge(date={self.date}, puzzle={self.puzzle_id})"
