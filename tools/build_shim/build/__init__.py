from __future__ import annotations

import importlib
import sys
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Any, Dict

_SHIM_ROOT = Path(__file__).resolve().parent.parent


@contextmanager
def _without_shim() -> contextmanager[None]:
    saved_path = list(sys.path)
    saved_module = sys.modules.pop("build", None)
    try:
        sys.path = [p for p in sys.path if Path(p).resolve() != _SHIM_ROOT]
        yield
    finally:
        sys.path = saved_path
        if saved_module is not None:
            sys.modules["build"] = saved_module


def _load_real_build() -> ModuleType:
    with _without_shim():
        return importlib.import_module("build")


_real = _load_real_build()
_globals: Dict[str, Any] = {name: getattr(_real, name) for name in dir(_real)}
globals().update(_globals)
__all__ = getattr(_real, "__all__", list(_globals))
__doc__ = getattr(_real, "__doc__")
