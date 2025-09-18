from __future__ import annotations

import os
from typing import Literal

from .engines import DokusanEngine, Engine, GridSpec

EngineName = Literal["dokusan"]


def get_engine_for(spec: GridSpec, *, source: EngineName | None = None) -> Engine:
    """
    Select engine based on source or environment variable PUZZLE_ENGINE_9.
    For now, supports only 9×9 dokusan stub.
    """
    if source is None:
        env_val = os.getenv("PUZZLE_ENGINE_9") if spec.size == 9 else None
        if env_val is None:
            src: EngineName = "dokusan"
        elif env_val == "dokusan":
            src = "dokusan"
        else:
            raise ValueError(f"Unknown engine source in env: {env_val}")
    else:
        src = source

    if src == "dokusan":
        eng = DokusanEngine()
        if not eng.supports(spec=spec):
            raise ValueError(f"Engine 'dokusan' does not support spec size={spec.size}")
        return eng
    raise ValueError(f"Unknown engine source: {src}")
