"""Unit tests for GUI threading helpers."""

from __future__ import annotations

import threading

import pytest

try:  # pragma: no cover - optional Qt dependency
    from visbrain.qt import QtCore, QtWidgets
except Exception:  # pragma: no cover - optional Qt dependency
    QtCore = QtWidgets = None

import visbrain.gui.threading as gui_threading


pytestmark = [
    pytest.mark.skipif(QtWidgets is None, reason="Qt bindings are unavailable"),
]


def test_invoke_in_gui_thread_without_qt(monkeypatch):
    """When Qt is unavailable the callable executes inline."""

    monkeypatch.setattr(gui_threading, "QtWidgets", None)
    monkeypatch.setattr(gui_threading, "QtCore", None)

    def fail(*args, **kwargs):  # pragma: no cover - defensive
        raise AssertionError("call_on_main_thread should not be used without Qt")

    monkeypatch.setattr(gui_threading, "call_on_main_thread", fail)

    executed = []

    def marker(value: int) -> int:
        executed.append(threading.current_thread())
        return value + 1

    result = gui_threading.invoke_in_gui_thread(marker, 41)
    assert result == 42
    assert executed
    assert executed[0] is threading.current_thread()


def test_invoke_in_gui_thread_uses_gui_thread(qtbot):
    """Callable dispatched from a worker thread runs on the GUI thread."""

    app = QtWidgets.QApplication.instance()
    assert app is not None

    gui_thread = app.thread()
    assert gui_thread is not None

    observed = []

    def worker() -> None:
        def record() -> None:
            observed.append(QtCore.QThread.currentThread())

        gui_threading.invoke_in_gui_thread(record)

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join(timeout=2)

    qtbot.waitUntil(lambda: bool(observed), timeout=1000)
    assert observed[0] is gui_thread
