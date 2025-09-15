from __future__ import annotations

import random

from .base import Engine, GridSpec


class DokusanEngine(Engine):
    """
    Simple 9×9-capable engine placeholder.
    For now, uses deterministic PRNG for reproducibility and a trivial solver stub.
    Replace with a real solver/generator in later phases.
    """

    def _rand_grid(self, *, spec: GridSpec, seed: int | None) -> tuple[str, str]:
        rng = random.Random(seed)
        n = spec.size * spec.size
        # Produce a pseudo-solution of 1..9 cycling; adequate placeholder for tests.
        solution = "".join(str((i % spec.size) + 1) for i in range(n))
        # Create givens by zeroing out ~60% cells deterministically
        givens_list = list(solution)
        for i in range(n):
            if rng.random() < 0.6:
                givens_list[i] = "0"
        givens = "".join(givens_list)
        return givens, solution

    def generate(
        self, *, spec: GridSpec, difficulty: str, seed: int | None = None
    ) -> tuple[str, str, float]:
        if spec.size != 9:
            raise ValueError("DokusanEngine currently supports only 9×9 in this stub")
        givens, solution = self._rand_grid(spec=spec, seed=seed)
        metric = self.rate_difficulty(spec=spec, grid=givens)
        return givens, solution, metric

    def solve(self, *, spec: GridSpec, grid: str) -> str | None:
        # Stub: return a cyclic "solution" if length matches; real solver to come later
        if len(grid) != spec.size * spec.size:
            return None
        return "".join(str((i % spec.size) + 1) for i in range(spec.size * spec.size))

    def has_unique_solution(self, *, spec: GridSpec, grid: str) -> bool:
        # Stub uniqueness: treat any properly sized grid as uniquely solvable
        return len(grid) == spec.size * spec.size

    def rate_difficulty(self, *, spec: GridSpec, grid: str) -> float:
        # Simple heuristic: fewer givens = higher metric
        total = spec.size * spec.size
        filled = sum(1 for ch in grid if ch != "0")
        empties = total - filled
        return empties / total
