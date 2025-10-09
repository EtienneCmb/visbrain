"""Shared helpers for running blocking IO in background threads."""

from __future__ import annotations

import logging
import os
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Lock
from typing import Any, Callable, Optional, TypeVar

try:  # pragma: no cover - optional Qt dependency
    from visbrain.qt import QtCore, QtWidgets
except Exception:  # pragma: no cover - optional Qt dependency
    QtCore = QtWidgets = None  # type: ignore[assignment]

try:  # pragma: no cover - optional configuration dependency
    import visbrain.config as _config
except Exception:  # pragma: no cover - optional configuration dependency
    _config = None  # type: ignore[assignment]

logger = logging.getLogger("visbrain")

_T = TypeVar("_T")
_EXECUTOR: ThreadPoolExecutor | None = None
_EXECUTOR_LOCK = Lock()
_BACKGROUND_ENVVAR = "VISBRAIN_BACKGROUND_WORKERS"


def _parse_env_flag(value: str) -> Optional[bool]:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return None


def _background_enabled() -> bool:
    """Return whether background workers should be used."""

    env_value = os.getenv(_BACKGROUND_ENVVAR)
    if env_value is not None:
        parsed = _parse_env_flag(env_value)
        if parsed is not None:
            return parsed
        logger.error(
            "Invalid value for %s: %s", _BACKGROUND_ENVVAR, env_value
        )

    if _config is not None:
        get_config = getattr(_config, "get_config", None)
        if callable(get_config):
            try:
                cfg = get_config()
            except Exception:  # pragma: no cover - defensive
                logger.debug(
                    "Fetching visbrain configuration failed", exc_info=True
                )
            else:
                attr = getattr(cfg, "background_workers", None)
                if attr is not None:
                    return bool(attr)

        attr = getattr(_config, "background_workers", None)
        if attr is not None:
            return bool(attr)

    return True


def _get_executor() -> ThreadPoolExecutor:
    """Return the global :class:`~ThreadPoolExecutor` instance."""

    global _EXECUTOR
    if _EXECUTOR is None:
        with _EXECUTOR_LOCK:
            if _EXECUTOR is None:
                _EXECUTOR = ThreadPoolExecutor(
                    max_workers=1,
                    thread_name_prefix="sleep-loader",
                )
    return _EXECUTOR


def shutdown_loader_threads(*, wait: bool = False) -> None:
    """Shut down the shared executor used for loader tasks."""

    global _EXECUTOR
    executor = _EXECUTOR
    if executor is not None:
        executor.shutdown(wait=wait)
        _EXECUTOR = None


def _execute_inline(
    function: Callable[..., _T], *args: Any, **kwargs: Any
) -> Future[_T]:
    """Execute ``function`` synchronously while returning a resolved future."""

    future: Future[_T] = Future()
    try:
        result = function(*args, **kwargs)
    except BaseException as exc:  # pragma: no cover - defensive
        future.set_exception(exc)
    else:
        future.set_result(result)
    return future


def run_in_loader_thread(
    function: Callable[..., _T],
    *args: Any,
    **kwargs: Any,
) -> Future[_T]:
    """Execute ``function`` in the shared background executor."""

    if not _background_enabled():
        return _execute_inline(function, *args, **kwargs)

    executor = _get_executor()
    return executor.submit(function, *args, **kwargs)


def call_on_main_thread(func: Callable[..., _T], *args: Any, **kwargs: Any) -> _T:
    """Execute *func* on the Qt GUI thread and return its result."""

    if QtCore is None or QtWidgets is None:
        return func(*args, **kwargs)

    app = QtWidgets.QApplication.instance()
    if app is None:
        return func(*args, **kwargs)

    gui_thread = app.thread()
    if gui_thread is None or gui_thread is QtCore.QThread.currentThread():
        return func(*args, **kwargs)

    class _Invoker(QtCore.QObject):  # pragma: no cover - requires Qt GUI thread
        def __init__(self) -> None:
            super().__init__()
            self._result: Any = None
            self._error: Optional[BaseException] = None

        @QtCore.Slot()
        def invoke(self) -> None:
            try:
                self._result = func(*args, **kwargs)
            except BaseException as exc:  # pragma: no cover - defensive
                self._error = exc

        def result(self) -> Any:
            if self._error is not None:
                raise self._error
            return self._result

    proxy = _Invoker()
    proxy.moveToThread(gui_thread)
    QtCore.QMetaObject.invokeMethod(
        proxy,
        "invoke",
        QtCore.Qt.BlockingQueuedConnection,
    )
    return proxy.result()


__all__ = [
    "run_in_loader_thread",
    "call_on_main_thread",
    "shutdown_loader_threads",
]

