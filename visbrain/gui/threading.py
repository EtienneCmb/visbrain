"""Threading utilities shared across Qt-based controllers."""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from visbrain.io.background import call_on_main_thread

try:  # pragma: no cover - optional Qt dependency
    from visbrain.qt import QtCore, QtWidgets
except Exception:  # pragma: no cover - optional Qt dependency
    QtCore = QtWidgets = None  # type: ignore[assignment]

_T = TypeVar("_T")


def invoke_in_gui_thread(
    function: Callable[..., _T], *args: Any, **kwargs: Any
) -> _T:
    """Execute *function* on the Qt GUI thread when available."""

    if QtCore is None or QtWidgets is None:
        return function(*args, **kwargs)

    app = QtWidgets.QApplication.instance()
    if app is None:
        return function(*args, **kwargs)

    gui_thread = app.thread()
    if gui_thread is None or gui_thread is QtCore.QThread.currentThread():
        return function(*args, **kwargs)

    return call_on_main_thread(function, *args, **kwargs)


__all__ = ["invoke_in_gui_thread"]

