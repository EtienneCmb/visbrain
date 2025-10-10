"""Helpers to load the original pytest-qt plugin when available."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import site
import sys
from pathlib import Path
from types import ModuleType
from typing import Iterable

_STUB_DIR = Path(__file__).resolve().parent


def _candidate_paths() -> Iterable[Path]:
    for path in site.getsitepackages():
        yield Path(path)
    user = site.getusersitepackages()
    if user:
        yield Path(user)


def load_real_plugin() -> ModuleType:
    """Return the real ``pytestqt.plugin`` module from site-packages."""

    for root in _candidate_paths():
        spec = importlib.machinery.PathFinder.find_spec("pytestqt.plugin", [str(root)])
        if spec is None or spec.origin is None:
            continue
        origin = Path(spec.origin).resolve()
        if origin.is_relative_to(_STUB_DIR):
            continue
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        sys.modules["pytestqt.plugin"] = module
        return module
    msg = "Could not locate the real pytestqt.plugin module"
    raise ImportError(msg)
