"""Qt binding compatibility layer for Visbrain.

This module centralizes access to Qt modules so that the rest of the codebase
can rely on a single import location while we transition away from the PyQt5
API.  It prefers the PySide6 binding but gracefully falls back to PyQt5 for
legacy environments.
"""
from __future__ import annotations

import atexit
import importlib
import os
import logging
import weakref
from types import SimpleNamespace
from typing import Any, Optional

logger = logging.getLogger("visbrain")

# Exposed names; they are populated once a binding is found.
QtCore: Any = None
QtGui: Any = None
QtWidgets: Any = None
Qt: Any = None

QT_API = None

_REQUIRED_MODULES = ("QtCore", "QtGui", "QtWidgets")
_OPTIONAL_MODULES = ("QtSvg", "QtPrintSupport")
_BINDINGS = ("PySide6", "PyQt5")


def _build_qt_namespace(modules: dict[str, object]) -> SimpleNamespace:
    """Aggregate Qt classes into a PyQt5-like ``Qt`` namespace."""
    namespace = SimpleNamespace()
    for module in modules.values():
        if module is None:
            continue
        for attr in dir(module):
            if attr.startswith("_"):
                continue
            value = getattr(module, attr)
            # Limit ourselves to Qt enums, classes and helper namespaces.
            if attr[0].isupper() or attr.startswith("Qt"):
                setattr(namespace, attr, value)
    return namespace


def _install_stub_binding() -> None:
    """Populate module globals with inert Qt stand-ins."""

    global QtCore, QtGui, QtWidgets, Qt, QT_API

    class _StubBase:
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
            pass

        def __getattr__(self, _name: str) -> "_StubBase":  # pragma: no cover
            return self.__class__()

        def __call__(
            self, *args: Any, **kwargs: Any
        ) -> "_StubBase":  # pragma: no cover
            return self.__class__()

    class _StubApplication(_StubBase):
        @staticmethod
        def instance() -> None:  # pragma: no cover
            return None

        def quit(self) -> None:  # pragma: no cover
            pass

        @staticmethod
        def setQuitOnLastWindowClosed(_value: bool) -> None:  # pragma: no cover
            pass

    class _StubWidget(_StubBase):
        Window = 0
        WindowTitleHint = 0

    class _StubDialog(_StubBase):
        pass

    class _StubAction(_StubBase):
        pass

    class _StubSignal(_StubBase):
        pass

    def _create_signal(*_args: Any, **_kwargs: Any) -> _StubSignal:  # pragma: no cover
        return _StubSignal()

    def _slot(*_args: Any, **_kwargs: Any):  # pragma: no cover
        return lambda func: func

    class _StubEnum:
        def __getattr__(self, _name: str) -> int:  # pragma: no cover
            return 0

    QtCore = SimpleNamespace(
        QObject=_StubBase,
        QCoreApplication=SimpleNamespace(closingDown=lambda: False),
        pyqtSignal=_create_signal,
        Signal=_create_signal,
        Slot=_slot,
        Qt=_StubEnum(),
    )
    QtGui = SimpleNamespace(QAction=_StubAction, QPalette=_StubBase)
    QtWidgets = SimpleNamespace(
        QApplication=_StubApplication,
        QWidget=_StubWidget,
        QDialog=_StubDialog,
    )
    Qt = _build_qt_namespace({"QtCore": QtCore, "QtGui": QtGui, "QtWidgets": QtWidgets})
    QT_API = "stub"


def _import_binding() -> None:
    """Import the preferred Qt binding and populate module globals."""
    global QtCore, QtGui, QtWidgets, Qt, QT_API

    stub_pref = os.environ.get("VISBRAIN_USE_QT_STUBS", "").strip().lower()
    if stub_pref in {"1", "true", "yes", "on"}:
        logger.debug(
            "Using stub Qt binding due to VISBRAIN_USE_QT_STUBS=%s",
            stub_pref,
        )
        _install_stub_binding()
        return

    for binding in _BINDINGS:
        modules: dict[str, object] = {}
        try:
            for name in _REQUIRED_MODULES:
                modules[name] = importlib.import_module(f"{binding}.{name}")
        except ImportError:
            continue

        for name in _OPTIONAL_MODULES:
            try:
                modules[name] = importlib.import_module(f"{binding}.{name}")
            except ImportError:
                modules[name] = None

        QtCore = modules["QtCore"]
        QtGui = modules["QtGui"]
        QtWidgets = modules["QtWidgets"]
        Qt = _build_qt_namespace(modules)
        QT_API = binding
        logger.debug("Using %s Qt binding", binding)
        return

    if stub_pref not in {"0", "false", "no", "off"}:
        logger.warning(
            "Falling back to stub Qt binding because no supported binding could be "
            "imported.",
        )
        _install_stub_binding()
        return

    raise ImportError(
        "Unable to import a supported Qt binding. Install PySide6 (preferred) "
        "or PyQt5."
    )


_import_binding()

if QtWidgets is not None and QtGui is not None:
    if not hasattr(QtWidgets, "QAction") and hasattr(QtGui, "QAction"):
        QtWidgets.QAction = QtGui.QAction  # type: ignore[attr-defined]

_QAPP_CLEANUP_REGISTERED = False


class _QObjectLifecycle:
    """Track whether a :class:`~QtCore.QObject` is still alive."""

    def __init__(self) -> None:
        self._ref: weakref.ReferenceType[Any] | None = None
        self._alive = False

    def watch(self, obj: Optional[Any]) -> None:
        """Start tracking *obj* and mark it as alive."""

        if obj is None:
            return
        current = self._ref() if self._ref is not None else None
        if current is obj and self._alive:
            return

        def _mark_dead(*_args: object) -> None:
            self._alive = False
            self._ref = None

        try:
            obj.destroyed.connect(_mark_dead)  # type: ignore[union-attr]
        except Exception:  # pragma: no cover - defensive fallback
            pass
        self._ref = weakref.ref(obj)
        self._alive = True

    def get(self) -> Optional[Any]:
        """Return the tracked object if it is still alive."""

        if not self._alive or self._ref is None:
            return None
        instance = self._ref()
        if instance is None:
            self._alive = False
            self._ref = None
            return None
        return instance


_QAPP_LIFECYCLE = _QObjectLifecycle()


def _shutdown_qapplication() -> None:
    """Attempt to gracefully close the tracked Qt application."""

    if QtCore.QCoreApplication.closingDown():  # pragma: no cover - during exit
        return

    tracked = _QAPP_LIFECYCLE.get()
    app = tracked if isinstance(tracked, QtWidgets.QApplication) else None
    if app is None:
        app = QtWidgets.QApplication.instance()
    if app is None:
        return

    set_quit = getattr(QtWidgets.QApplication, "setQuitOnLastWindowClosed", None)
    if callable(set_quit):  # pragma: no branch - guard missing Qt API
        try:
            set_quit(True)
        except Exception:  # pragma: no cover - best effort cleanup
            pass

    quit_method = getattr(app, "quit", None)
    if callable(quit_method):
        quit_method()


def guard_qapp_lifecycle() -> None:
    """Configure the Qt application for deterministic shutdown semantics."""

    set_quit = getattr(QtWidgets.QApplication, "setQuitOnLastWindowClosed", None)
    if callable(set_quit):  # pragma: no branch - guard missing Qt API
        try:
            set_quit(False)
        except Exception:  # pragma: no cover - best effort cleanup
            pass
    app = QtWidgets.QApplication.instance()
    if app is not None:
        _QAPP_LIFECYCLE.watch(app)

    global _QAPP_CLEANUP_REGISTERED
    if not _QAPP_CLEANUP_REGISTERED:
        atexit.register(_shutdown_qapplication)
        _QAPP_CLEANUP_REGISTERED = True


__all__ = ["QtCore", "QtGui", "QtWidgets", "Qt", "QT_API", "guard_qapp_lifecycle"]
