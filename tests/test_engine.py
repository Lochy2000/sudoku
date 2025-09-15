from puzzle.services.engines import GridSpec
from puzzle.services.factory import get_engine_for


def test_engine_generate_and_solve_deterministic() -> None:
    spec = GridSpec(size=9, box_h=3, box_w=3)
    engine = get_engine_for(spec)

    givens1, solution1, metric1 = engine.generate(spec=spec, difficulty="medium", seed=42)
    givens2, solution2, metric2 = engine.generate(spec=spec, difficulty="medium", seed=42)

    assert givens1 == givens2
    assert solution1 == solution2
    assert metric1 == metric2

    assert len(givens1) == 81 and len(solution1) == 81
    assert 0 <= metric1 <= 1

    solved = engine.solve(spec=spec, grid=givens1)
    assert solved is not None and len(solved) == 81

    assert engine.has_unique_solution(spec=spec, grid=givens1) is True
