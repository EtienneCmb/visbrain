"""Unit tests ensuring dialogs execute on the GUI thread when required."""

from __future__ import annotations

import threading

import pytest

from visbrain.io.dialog import dialog_color, dialog_load, dialog_save

try:  # pragma: no cover - optional Qt dependency
    from visbrain.qt import QtCore, QtWidgets
except Exception:  # pragma: no cover - optional Qt dependency
    QtCore = QtWidgets = None


pytestmark = [
    pytest.mark.skipif(QtWidgets is None, reason="Qt bindings are unavailable"),
]


def _spawn_worker(target) -> None:
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout=2)


def test_dialog_save_runs_on_gui_thread(monkeypatch, qtbot):
    """Save dialogs opened from workers execute on the GUI thread."""

    app = QtWidgets.QApplication.instance()
    assert app is not None

    threads = []

    def fake_get_save_file(*args, **kwargs):
        threads.append(QtCore.QThread.currentThread())
        return "", ""

    monkeypatch.setattr(QtWidgets.QFileDialog, "getSaveFileName", fake_get_save_file)

    _spawn_worker(lambda: dialog_save(None, "Save", "file", ["*.*"]))

    qtbot.waitUntil(lambda: bool(threads), timeout=1000)
    assert all(thread is app.thread() for thread in threads)


def test_dialog_load_runs_on_gui_thread(monkeypatch, qtbot):
    """Open dialogs opened from workers execute on the GUI thread."""

    app = QtWidgets.QApplication.instance()
    assert app is not None

    threads = []

    def fake_get_open_file(*args, **kwargs):
        threads.append(QtCore.QThread.currentThread())
        return "", ""

    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", fake_get_open_file)

    _spawn_worker(lambda: dialog_load(None, "Open", "file", ["*.*"]))

    qtbot.waitUntil(lambda: bool(threads), timeout=1000)
    assert all(thread is app.thread() for thread in threads)


def test_dialogs_accept_non_widget_parent(monkeypatch):
    """Dialogs can be invoked with non-Qt parents (e.g., PySide6)."""

    sentinel = object()
    parents = []

    def fake_get_save_file(parent, *args, **kwargs):
        parents.append(("save", parent))
        return "", ""

    def fake_get_open_file(parent, *args, **kwargs):
        parents.append(("open", parent))
        return "", ""

    monkeypatch.setattr(QtWidgets.QFileDialog, "getSaveFileName", fake_get_save_file)
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", fake_get_open_file)

    dialog_save(sentinel, "Save", "file", ["*.*"])
    dialog_load(sentinel, "Open", "file", ["*.*"])

    assert parents == [("save", None), ("open", None)]


def test_dialog_color_runs_on_gui_thread(monkeypatch, qtbot):
    """Color dialogs execute on the GUI thread even from workers."""

    app = QtWidgets.QApplication.instance()
    assert app is not None

    threads = []

    class _Color:
        def name(self) -> str:  # pragma: no cover - simple accessor
            return "#000000"

    def fake_get_color(*args, **kwargs):
        threads.append(QtCore.QThread.currentThread())
        return _Color()

    monkeypatch.setattr(QtWidgets.QColorDialog, "getColor", fake_get_color)

    _spawn_worker(dialog_color)

    qtbot.waitUntil(lambda: bool(threads), timeout=1000)
    assert all(thread is app.thread() for thread in threads)
