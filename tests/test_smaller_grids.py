from typing import Any

from puzzle.services.engines import GridSpec
from puzzle.services.factory import get_engine_for
from puzzle.services.generation import generate_template


def test_engine_supports_4x4_and_6x6() -> None:
    for size, box_h, box_w in [(4, 2, 2), (6, 2, 3)]:
        spec = GridSpec(size=size, box_h=box_h, box_w=box_w)
        eng = get_engine_for(spec)
        g, s, m = eng.generate(spec=spec, difficulty="medium", seed=7)
        assert len(g) == size * size and len(s) == size * size
        assert eng.solve(spec=spec, grid=g) is not None
        assert eng.has_unique_solution(spec=spec, grid=g) is True


def test_generate_template_for_smaller_grids(db: Any) -> None:
    for size, box_h, box_w in [(4, 2, 2), (6, 2, 3)]:
        res = generate_template(size=size, box_h=box_h, box_w=box_w, difficulty="medium", seed=11)
        t = res.template
        assert t.size == size and t.box_h == box_h and t.box_w == box_w
        assert len(t.givens) == size * size and len(t.solution) == size * size
