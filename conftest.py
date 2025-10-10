"""Pytest configuration for Visbrain.

This module centralizes headless Qt configuration and test markers so all
collected test modules behave consistently regardless of their location in the
repository.
"""
from __future__ import annotations

import os
import warnings
import importlib
from pathlib import Path
from typing import Iterable

import pytest

# Ensure coverage flags remain available when plugin auto-loading is disabled.
pytest_plugins = ["pytest_cov"]

# -----------------------------------------------------------------------------
# Headless Qt configuration
# -----------------------------------------------------------------------------
# Force Qt to use an offscreen platform so GUI tests can run in headless
# environments (such as CI workers). Matplotlib defaults to a Qt-backed GUI
# when the bindings are available, which leads to aborts on CI runners without a
# display. Prefer the non-interactive ``Agg`` backend so simple import tests do
# not crash the interpreter.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLBACKEND", "Agg")

try:
    from visbrain.config import configure_headless
except Exception:  # pragma: no cover - defensive in CI without GUI libs
    CONFIG = None
else:
    CONFIG = configure_headless()

_REPO_ROOT = Path(__file__).parent.resolve()
_REPO_PACKAGE_ROOT = (_REPO_ROOT / "visbrain").resolve()

_GUI_RELATIVE_PATHS = (
    Path("gui"),
    Path("objects") / "tests",
    Path("utils") / "gui" / "tests",
    Path("io") / "tests",
    Path("utils") / "sleep" / "tests",
    Path("utils") / "tests",
    Path("tests") / "test_gui_lifecycle.py",
    Path("tests") / "test_icons.py",
    Path("tests") / "test_opengl_diagnostics.py",
    Path("resources") / "tests",
)


def _resolve_installed_package_root() -> Path:
    """Return the resolved installation path of the :mod:`visbrain` package."""

    try:
        module = importlib.import_module("visbrain")
    except Exception:
        return _REPO_PACKAGE_ROOT

    module_file = getattr(module, "__file__", None)
    if module_file is None:
        return _REPO_PACKAGE_ROOT
    return Path(module_file).resolve().parent


def _build_gui_marker_paths(package_roots: Iterable[Path]) -> tuple[Path, ...]:
    """Return normalized GUI marker paths for the given *package_roots*."""

    markers: list[Path] = []
    seen: set[Path] = set()
    for root in package_roots:
        resolved_root = Path(root).resolve()
        for relative in _GUI_RELATIVE_PATHS:
            candidate = (resolved_root / relative).resolve()
            if candidate not in seen:
                markers.append(candidate)
                seen.add(candidate)
    return tuple(markers)


_GUI_MARKER_PATHS = _build_gui_marker_paths(
    (_REPO_PACKAGE_ROOT, _resolve_installed_package_root())
)


def _expression_allows_gui(config: pytest.Config) -> bool:
    """Return True when GUI-heavy tests should be collected."""

    expr = (getattr(config.option, "markexpr", "") or "").lower()
    if not expr:
        return True

    if "not gui" in expr and "gui" not in expr.replace("not gui", ""):
        return False
    if "not screenshot" in expr and "screenshot" not in expr.replace(
        "not screenshot", ""
    ):
        return False

    # When the expression explicitly targets GUI or screenshot markers we keep
    # them; otherwise, err on the side of collecting to preserve legacy
    # behaviour.
    if "gui" in expr or "screenshot" in expr:
        return True
    return True


_RUNNING_GUI_TESTS = True


def pytest_configure(config: pytest.Config) -> None:
    """Register the custom GUI and screenshot markers."""
    config.addinivalue_line(
        "markers", "gui: tests that require a Qt/OpenGL stack"
    )
    config.addinivalue_line(
        "markers",
        "screenshot: Qt/VisPy screenshot regression tests",
    )
    global _RUNNING_GUI_TESTS
    _RUNNING_GUI_TESTS = _expression_allows_gui(config)
    if _RUNNING_GUI_TESTS:
        if os.environ.get("VISBRAIN_ENABLE_PYTEST_QT"):
            try:
                config.pluginmanager.import_plugin("pytestqt.plugin")
            except Exception as exc:  # pragma: no cover - environment-specific
                warnings.warn(
                    "pytest-qt plugin could not be imported; GUI tests will be skipped."
                    f"\nReason: {exc}",
                    RuntimeWarning,
                )
                _RUNNING_GUI_TESTS = False
        else:
            warnings.warn(
                "GUI tests were requested but pytest-qt autoloading is disabled."
                " Set VISBRAIN_ENABLE_PYTEST_QT=1 to enable them.",
                RuntimeWarning,
            )
            _RUNNING_GUI_TESTS = False


def _is_under(path: Path, parents: Iterable[Path]) -> bool:
    """Return ``True`` if *path* is located under any of *parents*."""
    normalized_path = Path(path).resolve()
    for parent in parents:
        normalized_parent = Path(parent).resolve()
        try:
            normalized_path.relative_to(normalized_parent)
        except ValueError:
            continue
        else:
            return True
    return False


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Mark tests under GUI-specific paths with the ``gui`` marker."""
    for item in items:
        item_path = Path(str(item.fspath)).resolve()
        if _is_under(item_path, _GUI_MARKER_PATHS):
            item.add_marker("gui")


def pytest_ignore_collect(
    collection_path: Path,
    path=None,
    config: pytest.Config | None = None,  # type: ignore[override]
):
    """Skip importing GUI-heavy test modules when they are deselected."""
    if config is None and path is not None:  # pragma: no branch - old pytest signature
        config = path  # type: ignore[assignment]
    if config is not None and _RUNNING_GUI_TESTS:
        return False
    if config is None and _RUNNING_GUI_TESTS:
        return False
    normalized_collection_path = Path(collection_path).resolve()
    return _is_under(normalized_collection_path, _GUI_MARKER_PATHS)
