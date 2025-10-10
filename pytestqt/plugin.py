"""Minimal pytest-qt shim used when a GUI stack is unavailable."""
from __future__ import annotations

import os
import sys
from typing import Any

import pytest

if os.environ.get("VISBRAIN_ENABLE_PYTEST_QT"):
    from ._real import load_real_plugin

    _real = load_real_plugin()
    globals().update(_real.__dict__)
    sys.modules[__name__] = _real
else:

    def pytest_addoption(parser: pytest.Parser) -> None:  # type: ignore[name-defined]
        parser.addini(
            "qt_api",
            "Qt binding to use for GUI tests (stubbed by visbrain).",
        )

    def pytest_configure(config: pytest.Config) -> None:  # pragma: no cover
        """Expose the same markers as the real pytest-qt plugin."""

        config.addinivalue_line("markers", "gui: tests that require a Qt/OpenGL stack")
        config.addinivalue_line(
            "markers",
            "qt_noop: placeholder marker emitted by the pytest-qt shim",
        )
        config.addinivalue_line(
            "markers",
            "qt_stub: pytest-qt shim marker for headless execution",
        )

    @pytest.fixture(scope="session")
    def qtbot() -> Any:  # pragma: no cover - defensive stub
        """Provide a stand-in qtbot fixture that skips GUI-dependent tests."""

        pytest.skip("Qt bindings are unavailable in this environment")
