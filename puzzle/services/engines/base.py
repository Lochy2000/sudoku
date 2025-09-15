from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class GridSpec:
    size: int
    box_h: int
    box_w: int


class Engine(ABC):
    """Abstract interface for Sudoku engines (generation, solving, rating)."""

    @abstractmethod
    def generate(
        self, *, spec: GridSpec, difficulty: str, seed: int | None = None
    ) -> tuple[str, str, float]:
        """
        Returns (givens, solution, difficulty_metric) for the requested grid.
        - givens/solution are 1D strings length spec.size*spec.size ('0' for empty in givens)
        - difficulty_metric is an engine-defined float used to map to a label
        """

    @abstractmethod
    def solve(self, *, spec: GridSpec, grid: str) -> str | None:
        """Return solved board string if solvable, else None."""

    @abstractmethod
    def has_unique_solution(self, *, spec: GridSpec, grid: str) -> bool:
        """Return True if the given grid has exactly one solution."""

    @abstractmethod
    def rate_difficulty(self, *, spec: GridSpec, grid: str) -> float:
        """Return a difficulty metric for the given grid."""
