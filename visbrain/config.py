"""Configuration and runtime helpers for Visbrain."""
from __future__ import annotations

import importlib
import getopt
import logging
import os
import sys
import warnings
from contextlib import contextmanager
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Callable, Iterator, Mapping, MutableMapping, Optional, Sequence

_VISPY_BASE_ERROR: Exception | None

try:
    import vispy
except Exception as exc:  # pragma: no cover - defensive against broken installs
    vispy = None  # type: ignore[assignment]
    _VISPY_BASE_ERROR = exc
else:
    _VISPY_BASE_ERROR = None

_VISPY_CONFIG_ERROR: Exception | None

try:
    vispy_config = vispy.config if vispy is not None else None
except Exception as exc:  # pragma: no cover - defensive
    vispy_config = None
    _VISPY_CONFIG_ERROR = exc
else:
    _VISPY_CONFIG_ERROR = None


def _load_vispy_app() -> Any:
    """Return the :mod:`vispy.app` module, allowing tests to monkeypatch imports."""

    return importlib.import_module("vispy.app")


_VISPY_APP_ERROR: Exception | None

try:
    visapp = _load_vispy_app()
except Exception as exc:  # pragma: no cover - exercised via diagnostics tests
    _VISPY_APP_ERROR = exc
    _VISPY_APP_ERROR_MESSAGE = (
        "VisPy backend is unavailable: %s" % exc
    )

    def _raise_vispy_unavailable(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError(_VISPY_APP_ERROR_MESSAGE) from _VISPY_APP_ERROR

    visapp = SimpleNamespace(
        application=SimpleNamespace(Application=_raise_vispy_unavailable),
        use_app=_raise_vispy_unavailable,
    )
else:
    _VISPY_APP_ERROR = None

from visbrain.utils.logging import set_log_level  # noqa: E402
from visbrain.utils.others import Profiler  # noqa: E402

from .qt import QT_API, QtWidgets, guard_qapp_lifecycle  # noqa: E402


logger = logging.getLogger("visbrain")


@dataclass
class VisPyDiagnostics:
    """Snapshot describing the current VisPy backend status."""

    requested_backend: str | None = None
    resolved_backend: str | None = None
    available: bool = False
    context_available: bool = False
    gl_version: str | None = None
    renderer: str | None = None
    error: str | None = None
    max_texture_size: int | None = None
    max_texture_3d_size: int | None = None
    max_texture_units: int | None = None
    shader_compiled: bool | None = None
    shader_error: str | None = None
    fallback_reason: str | None = None
    headless_attempts: list[dict[str, Any]] = field(default_factory=list)

    def payload(self) -> dict[str, Any]:
        """Return diagnostic metadata suitable for structured logging."""

        payload: dict[str, Any] = {
            "requested_backend": self.requested_backend,
            "resolved_backend": self.resolved_backend,
            "available": self.available,
            "context_available": self.context_available,
            "gl_version": self.gl_version,
            "renderer": self.renderer,
            "error": self.error,
            "max_texture_size": self.max_texture_size,
            "max_texture_3d_size": self.max_texture_3d_size,
            "max_texture_units": self.max_texture_units,
            "shader_compiled": self.shader_compiled,
            "shader_error": self.shader_error,
            "fallback_reason": self.fallback_reason,
        }
        if self.headless_attempts:
            payload["headless_attempts"] = [
                dict(item) for item in self.headless_attempts
            ]
        return payload


_VISPY_WARNING_MESSAGES: set[str] = set()
_HEADLESS_BACKENDS: Sequence[str] = ("egl", "osmesa")
_SHADER_PROBE_ENVVAR = "VISBRAIN_SHADER_PROBE"
_GL_CONTEXT_PROBE_ENVVAR = "VISBRAIN_GL_CONTEXT_PROBE"


def _format_exception(exc: BaseException) -> str:
    """Return a concise textual representation of *exc*."""

    return f"{exc.__class__.__name__}: {exc}" if exc else ""


def _warn_once(message: str) -> None:
    """Emit a warning once per unique *message*."""

    if message in _VISPY_WARNING_MESSAGES:
        return
    _VISPY_WARNING_MESSAGES.add(message)
    warnings.warn(message, UserWarning, stacklevel=3)


def _log_vispy_diagnostics(diag: VisPyDiagnostics) -> None:
    """Log diagnostics and warn the user when OpenGL is unavailable."""

    payload = {k: v for k, v in diag.payload().items() if v not in (None, "")}
    logger.info("vispy.probe %s", payload)
    if not diag.available or not diag.context_available:
        message = "VisPy backend unavailable or headless context missing"
        if diag.resolved_backend:
            message += f" (backend={diag.resolved_backend})"
        if diag.error:
            message += f": {diag.error}"
        _warn_once(message)


def _create_probe_canvas(diag: VisPyDiagnostics) -> Any | None:
    """Attempt to create a tiny hidden canvas to seed ``vispy.gloo.gl``."""
    try:
        # Ensure a Qt application exists for Qt-based backends (PySide/PyQt).
        # In some environments the vispy Canvas creation silently fails to
        # create a GL context if there is no QApplication, which leaves
        # vispy.gloo.gl.gl_info unset.
        cfg = get_config()
        try:
            cfg.get_qt_app(create=True, force=True)
        except Exception:
            # Best-effort: probing should never hard-fail here.
            pass

        # Prefer SceneCanvas when available (more robust context creation
        # across backends), otherwise fall back to the plain app.Canvas.
        try:
            from vispy import scene as _scene
        except Exception:
            _scene = None

        if _scene is not None and getattr(_scene, "SceneCanvas", None) is not None:
            try:
                canvas = _scene.SceneCanvas(show=False, size=(1, 1))
                # Make the canvas current: show briefly and pump events.
                try:
                    from vispy import app as _vapp
                    canvas.show()
                    _vapp.process_events()
                    _vapp.process_events()
                    # Enter/exit context once so backends mark it current.
                    try:
                        with canvas:
                            pass
                    except Exception:
                        pass
                except Exception:
                    pass
                return canvas
            except Exception as exc:
                # Fall through to try app.Canvas
                diag.error = diag.error or _format_exception(exc)

        from vispy import app as vispy_app
        canvas_cls = getattr(vispy_app, "Canvas", None)
        if canvas_cls is None:
            return None

        try:
            canvas = canvas_cls(show=False, size=(1, 1))
        except Exception as exc:  # pragma: no cover - best effort creation
            diag.error = diag.error or _format_exception(exc)
            return None

        # Make the canvas current: show briefly and pump events.
        try:
            from vispy import app as _vapp
            canvas.show()
            _vapp.process_events()
            _vapp.process_events()
            try:
                with canvas:
                    pass
            except Exception:
                pass
        except Exception:
            pass

        context = getattr(canvas, "context", None)
        setter = getattr(context, "set_current", None)
        if callable(setter):
            try:
                setter()
            except Exception:  # pragma: no cover - defensive
                pass

        return canvas
    except Exception as _unhandled_exc:  # pragma: no cover - belt and braces
        diag.error = diag.error or _format_exception(_unhandled_exc)
        return None


def _destroy_probe_canvas(canvas: Any | None) -> None:
    """Tear down a probe canvas created by :func:`_create_probe_canvas`."""

    if canvas is None:
        return

    for method_name in ("close", "delete", "destroy"):
        method = getattr(canvas, method_name, None)
        if callable(method):
            try:
                method()
            except Exception:  # pragma: no cover - defensive
                continue
            break


def _query_gl_capabilities(diag: VisPyDiagnostics) -> None:
    """Populate OpenGL information in-place on *diag*, using GLContext.capabilities."""
    try:
        from vispy.gloo.context import get_current_canvas
        from vispy import gloo
    except Exception as exc:
        diag.error = _format_exception(exc)
        diag.context_available = False
        return

    probe_canvas = None
    try:
        # Try to fetch the current canvas first
        canvas = None
        try:
            canvas = get_current_canvas()
        except Exception:
            canvas = None

        # If no valid canvas/context/capabilities, create a tiny probe canvas
        # to force context creation
        need_probe = (
            canvas is None or
            getattr(canvas, "context", None) is None or
            getattr(getattr(canvas, "context", None), "capabilities", None) is None
        )
        allow_probe = True
        raw_context_probe = os.environ.get(_GL_CONTEXT_PROBE_ENVVAR)
        if sys.platform == "darwin":
            allow_probe = False
        if raw_context_probe is not None:
            try:
                allow_probe = _parse_bool_flag(raw_context_probe)
            except ValueError:
                diag.error = diag.error or (
                    f"Invalid {_GL_CONTEXT_PROBE_ENVVAR} value: {raw_context_probe!r}"
                )
                allow_probe = False

        if need_probe and not allow_probe:
            diag.context_available = False
            if diag.error is None:
                if sys.platform == "darwin" and raw_context_probe is None:
                    diag.error = (
                        "OpenGL capability probe disabled by default on macOS "
                        f"(set {_GL_CONTEXT_PROBE_ENVVAR}=1 to force)"
                    )
                else:
                    diag.error = (
                        "OpenGL capability probe disabled "
                        f"(set {_GL_CONTEXT_PROBE_ENVVAR}=1 to force)"
                    )
            return

        if need_probe:
            probe_canvas = _create_probe_canvas(diag)
            try:
                canvas = get_current_canvas()
            except Exception:
                canvas = None
            # Fallback to the probe_canvas itself if VisPy did not mark it current
            if canvas is None and probe_canvas is not None:
                canvas = probe_canvas

        if canvas is None:
            diag.error = (
                "OpenGL capability probe unavailable: no active GL canvas"
            )
            diag.context_available = False
            return

        ctx = getattr(canvas, "context", None)
        # Ensure the context is marked current if possible
        if ctx is not None:
            setter = getattr(ctx, "set_current", None)
            if callable(setter):
                try:
                    setter()
                except Exception:
                    pass
        if ctx is None or getattr(ctx, "capabilities", None) is None:
            diag.error = (
                "OpenGL capability probe unavailable: no capabilities on context"
            )
            diag.context_available = False
            return

        caps = ctx.capabilities
        # We have a valid GL context + capabilities
        diag.context_available = True
        diag.gl_version = getattr(caps, "gl_version", None)
        diag.renderer = getattr(caps, "vendor", None) or getattr(caps, "renderer", None)
        diag.max_texture_size = getattr(caps, "max_texture_size", None)
        diag.max_texture_3d_size = getattr(caps, "max_3d_texture_size", None)
        diag.max_texture_units = getattr(caps, "max_texture_units", None)

        # --- Fallbacks: query GL directly if any fields are still None ---
        try:
            from vispy.gloo import gl as _gl
            # Strings: GL_VERSION, GL_RENDERER, GL_VENDOR
            def _get_gl_str(name, enum):
                try:
                    val = _gl.glGetString(enum)
                    if val is None:
                        return None
                    # VisPy may return bytes; normalize to str
                    return val.decode("utf-8") if hasattr(val, "decode") else str(val)
                except Exception:
                    return None

            if diag.gl_version is None and hasattr(_gl, "GL_VERSION"):
                diag.gl_version = _get_gl_str("GL_VERSION", _gl.GL_VERSION)
            if diag.renderer is None and hasattr(_gl, "GL_RENDERER"):
                # Prefer renderer; fall back to vendor if needed
                renderer = _get_gl_str("GL_RENDERER", _gl.GL_RENDERER)
                vendor = (
                    _get_gl_str("GL_VENDOR", getattr(_gl, "GL_VENDOR", None))
                    if hasattr(_gl, "GL_VENDOR")
                    else None
                )
                diag.renderer = renderer or vendor or diag.renderer

            # Integers: sizes / units
            def _get_gl_int(enum):
                try:
                    out = _gl.GLint()
                    _gl.glGetIntegerv(enum, out)
                    return int(out.value)
                except Exception:
                    try:
                        # Alternative return style in some backends
                        return int(_gl.glGetIntegerv(enum))
                    except Exception:
                        return None

            if diag.max_texture_size is None and hasattr(_gl, "GL_MAX_TEXTURE_SIZE"):
                diag.max_texture_size = _get_gl_int(_gl.GL_MAX_TEXTURE_SIZE)
            # 3D texture size constant may differ across backends; try a few
            if diag.max_texture_3d_size is None:
                for enum_name in (
                    "GL_MAX_3D_TEXTURE_SIZE",
                    "GL_MAX_TEXTURE_SIZE_3D",
                    "GL_MAX_3D_TEXTURE_SIZE_EXT",
                ):
                    if hasattr(_gl, enum_name):
                        val = _get_gl_int(getattr(_gl, enum_name))
                        if val is not None:
                            diag.max_texture_3d_size = val
                            break
            if diag.max_texture_units is None:
                for enum_name in (
                    "GL_MAX_TEXTURE_IMAGE_UNITS",
                    "GL_MAX_TEXTURE_UNITS",
                ):
                    if hasattr(_gl, enum_name):
                        val = _get_gl_int(getattr(_gl, enum_name))
                        if val is not None:
                            diag.max_texture_units = val
                            break
        except Exception:
            pass

        # --- Last resort: parse vispy.sys_info() for version/limits ---
        if (
            diag.gl_version is None
            or diag.max_texture_size is None
            or diag.renderer is None
        ):
            try:
                import re
                import vispy as _v
                info_txt = _v.sys_info()
                if isinstance(info_txt, str):
                    if diag.gl_version is None:
                        m = re.search(r"GL version:\s*([^\n]+)", info_txt)
                        if m:
                            diag.gl_version = m.group(1).strip()
                    if diag.max_texture_size is None:
                        m = re.search(r"MAX_TEXTURE_SIZE:\s*(\d+)", info_txt)
                        if m:
                            diag.max_texture_size = int(m.group(1))
            except Exception:
                pass

        # Optional: try basic shader compilation to verify pipeline health.
        raw_probe_flag = os.environ.get(_SHADER_PROBE_ENVVAR)
        enable_probe = False
        if raw_probe_flag is None:
            diag.shader_error = diag.shader_error or (
                f"Skipped shader probe (set {_SHADER_PROBE_ENVVAR}=1 to enable)"
            )
        else:
            try:
                enable_probe = _parse_bool_flag(raw_probe_flag)
            except ValueError:
                diag.shader_error = diag.shader_error or (
                    f"Invalid {_SHADER_PROBE_ENVVAR} value: {raw_probe_flag!r}"
                )
        if enable_probe:
            vert = "void main() { gl_Position = vec4(0.0); }"
            frag = "void main() { gl_FragColor = vec4(1.0); }"
            program_cls = getattr(gloo, "Program", None)
            if program_cls is None:
                diag.shader_compiled = False
                diag.shader_error = diag.shader_error or (
                    "vispy.gloo.Program is unavailable"
                )
            else:
                program = None
                try:
                    program = program_cls(vert, frag)
                    diag.shader_compiled = True
                    diag.shader_error = None
                except Exception as shader_exc:  # pragma: no cover - defensive
                    diag.shader_compiled = False
                    diag.shader_error = _format_exception(shader_exc)
                finally:
                    if program is not None:
                        for method_name in ("delete", "detach", "deactivate"):
                            method = getattr(program, method_name, None)
                            if callable(method):
                                try:
                                    method()
                                except Exception:  # pragma: no cover - defensive
                                    continue
                                break

    except Exception as exc:
        diag.error = _format_exception(exc)
        diag.context_available = False
    finally:
        _destroy_probe_canvas(probe_canvas)


def probe_vispy_environment(config: "VisbrainConfig") -> VisPyDiagnostics:
    """Inspect the VisPy backend and OpenGL runtime status."""

    diagnostics = VisPyDiagnostics(requested_backend=config.vispy_backend)
    if config._headless_attempts:
        diagnostics.headless_attempts = [
            dict(attempt) for attempt in config._headless_attempts
        ]
    if config._pending_fallback_reason:
        diagnostics.fallback_reason = config._pending_fallback_reason

    if _VISPY_APP_ERROR is not None:
        diagnostics.error = _format_exception(_VISPY_APP_ERROR)
        diagnostics.available = False
        diagnostics.context_available = False
        return diagnostics

    app = config.vispy_app
    created_app = False
    if app is None:
        try:
            app = visapp.application.Application(config.vispy_backend)
        except Exception as exc:  # pragma: no cover - guarded by tests
            diagnostics.error = _format_exception(exc)
            diagnostics.available = False
            diagnostics.context_available = False
            return diagnostics
        else:
            created_app = True

    diagnostics.available = True
    diagnostics.context_available = True
    diagnostics.resolved_backend = getattr(app, "backend_name", None) or (
        config.vispy_backend
    )

    _query_gl_capabilities(diagnostics)

    if created_app:
        # Reset temporary diagnostics application so we do not hold on to the
        # backend longer than necessary. The caller decides when to create a
        # long-lived VisPy application through :meth:`get_vispy_app`.
        del app

    return diagnostics


def select_headless_backend(
    config: "VisbrainConfig", *, candidates: Sequence[str] = _HEADLESS_BACKENDS
) -> tuple[str | None, str | None]:
    """Attempt to select an offscreen backend in headless environments."""

    attempts: list[dict[str, Any]] = []

    if _VISPY_APP_ERROR is not None:
        reason = _format_exception(_VISPY_APP_ERROR)
        payload = {
            "success": False,
            "backend": None,
            "error": reason,
        }
        attempts.append(payload)
        logger.info("vispy.headless %s", payload)
        config._headless_attempts = attempts
        return None, f"VisPy import failed: {reason}"

    for candidate in candidates:
        attempt = {"backend": candidate}
        try:
            visapp.application.Application(candidate)
        except Exception as exc:
            attempt["success"] = False
            attempt["error"] = _format_exception(exc)
            logger.info("vispy.headless %s", attempt)
            attempts.append(attempt)
            continue

        attempt["success"] = True
        logger.info("vispy.headless %s", attempt)
        attempts.append(attempt)

        if vispy_config is not None:
            try:
                vispy_config["default_backend"] = candidate
            except Exception as cfg_exc:  # pragma: no cover - defensive
                logger.debug(
                    "vispy.config update failed for backend %s: %s",
                    candidate,
                    _format_exception(cfg_exc),
                )
        config._headless_attempts = attempts
        reason = f"Configured headless backend '{candidate}'"
        return candidate, reason

    config._headless_attempts = attempts
    reason = "No suitable headless VisPy backend (EGL/OSMesa) was found."
    _warn_once(reason)
    logger.warning("vispy.headless %s", {"attempts": attempts, "success": False})
    return None, reason


@dataclass
class VisbrainConfig:
    """Container for runtime configuration and GUI application handles."""

    log_level: str = "info"
    log_search: str | None = None
    qt_api: str | None = QT_API
    vispy_backend: str | None = None
    show_gui: bool = True
    background_workers: bool = True
    mpl_render: bool = False
    theme: str = "dark"
    _pyqt_app: Optional[QtWidgets.QApplication] = field(
        default=None, init=False, repr=False
    )
    _vispy_app: Optional[visapp.Application] = field(
        default=None, init=False, repr=False
    )
    vispy_diagnostics: VisPyDiagnostics = field(
        default_factory=VisPyDiagnostics, init=False, repr=False
    )
    vispy_diagnostics_payload: dict[str, Any] = field(
        default_factory=dict, init=False, repr=False
    )
    _headless_attempts: list[dict[str, Any]] = field(
        default_factory=list, init=False, repr=False
    )
    _pending_fallback_reason: str | None = field(
        default=None, init=False, repr=False
    )

    def __post_init__(self) -> None:
        if self.vispy_backend is None and isinstance(self.qt_api, str):
            self.vispy_backend = self.qt_api.lower()
        self.apply_logging()
        self.refresh_vispy_diagnostics(log=False)

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------
    def apply_logging(self) -> None:
        """Apply the stored logging configuration."""

        set_log_level(self.log_level, match=self.log_search)

    def set_logging(
        self, *, level: str | None = None, match: str | None = None
    ) -> None:
        """Update and apply logging preferences."""

        if level is not None:
            self.log_level = level
        if match is not None:
            self.log_search = match
        self.apply_logging()

    def refresh_vispy_diagnostics(
        self, *, log: bool = True
    ) -> VisPyDiagnostics:
        """Update VisPy diagnostics for the current configuration."""

        diagnostics = probe_vispy_environment(self)
        self.vispy_diagnostics = diagnostics
        self.vispy_diagnostics_payload = diagnostics.payload()
        self._headless_attempts = [
            dict(attempt) for attempt in diagnostics.headless_attempts
        ]
        self._pending_fallback_reason = diagnostics.fallback_reason
        if log:
            _log_vispy_diagnostics(diagnostics)
        return diagnostics

    def apply_headless_backend_policy(self) -> None:
        """Attempt to select an offscreen backend when GUI display is disabled."""

        if self.show_gui:
            return
        previous = self.vispy_backend
        self._headless_attempts = []
        self._pending_fallback_reason = None
        fallback, reason = select_headless_backend(self)
        self._pending_fallback_reason = reason
        if fallback and fallback != previous:
            self.vispy_backend = fallback
            if self._vispy_app is not None:
                self._vispy_app = None
        self.refresh_vispy_diagnostics(log=True)

    # ------------------------------------------------------------------
    # Copy helpers
    # ------------------------------------------------------------------
    def copy(self) -> VisbrainConfig:
        """Return a shallow copy of the configuration."""

        duplicate = VisbrainConfig(
            log_level=self.log_level,
            log_search=self.log_search,
            qt_api=self.qt_api,
            vispy_backend=self.vispy_backend,
            background_workers=self.background_workers,
            show_gui=self.show_gui,
            mpl_render=self.mpl_render,
            theme=self.theme,
        )
        duplicate._pyqt_app = self._pyqt_app
        duplicate._vispy_app = self._vispy_app
        diag_data = vars(self.vispy_diagnostics).copy()
        diag_data["headless_attempts"] = [
            dict(attempt) for attempt in self.vispy_diagnostics.headless_attempts
        ]
        duplicate.vispy_diagnostics = VisPyDiagnostics(**diag_data)
        duplicate.vispy_diagnostics_payload = dict(self.vispy_diagnostics_payload)
        duplicate._headless_attempts = [
            dict(attempt) for attempt in self._headless_attempts
        ]
        duplicate._pending_fallback_reason = self._pending_fallback_reason
        return duplicate

    # ------------------------------------------------------------------
    # Backwards compatibility helpers
    # ------------------------------------------------------------------
    @property
    def show_pyqt_app(self) -> bool:
        """Return whether GUI resources should be created."""

        return self.show_gui

    @show_pyqt_app.setter
    def show_pyqt_app(self, enabled: bool) -> None:
        self.show_gui = bool(enabled)

    # ------------------------------------------------------------------
    # Qt application helpers
    # ------------------------------------------------------------------
    @property
    def pyqt_app(self) -> Optional[QtWidgets.QApplication]:
        """Return the cached Qt application instance."""

        return self._pyqt_app

    @pyqt_app.setter
    def pyqt_app(self, app: Optional[QtWidgets.QApplication]) -> None:
        self._pyqt_app = app

    def get_qt_app(
        self, *, create: bool = True, force: bool = False
    ) -> Optional[QtWidgets.QApplication]:
        """Return the active :class:`~QtWidgets.QApplication` instance."""

        app = QtWidgets.QApplication.instance()
        if app is None:
            if not create or (not self.show_gui and not force):
                self._pyqt_app = None
                return None
            app = QtWidgets.QApplication([""])

        self._pyqt_app = app
        guard_qapp_lifecycle()
        return app

    # ------------------------------------------------------------------
    # VisPy application helpers
    # ------------------------------------------------------------------
    @property
    def vispy_app(self) -> Optional[visapp.Application]:
        """Return the cached VisPy application instance."""

        return self._vispy_app

    @vispy_app.setter
    def vispy_app(self, app: Optional[visapp.Application]) -> None:
        self._vispy_app = app

    def get_vispy_app(
        self,
        backend: Optional[str] = None,
        *,
        create: bool = True,
        force: bool = False,
    ) -> Optional[visapp.Application]:
        """Return the active :class:`vispy.app.Application` instance."""

        if backend is not None:
            normalized = backend.lower() if isinstance(backend, str) else backend
            if normalized != self.vispy_backend:
                self.vispy_backend = normalized
                self._vispy_app = None

        if self._vispy_app is not None:
            self.refresh_vispy_diagnostics(log=False)
            return self._vispy_app

        if _VISPY_APP_ERROR is not None:
            diagnostics = VisPyDiagnostics(
                requested_backend=self.vispy_backend,
                available=False,
                context_available=False,
                error=_format_exception(_VISPY_APP_ERROR),
            )
            self.vispy_diagnostics = diagnostics
            self.vispy_diagnostics_payload = diagnostics.payload()
            self._headless_attempts = []
            self._pending_fallback_reason = diagnostics.fallback_reason
            _log_vispy_diagnostics(diagnostics)
            if force:
                raise RuntimeError(
                    "VisPy application backend is unavailable"
                ) from _VISPY_APP_ERROR
            return None

        if not create or (not self.show_gui and not force):
            return None

        try:
            self._vispy_app = visapp.application.Application(self.vispy_backend)
        except Exception as exc:
            diagnostics = VisPyDiagnostics(
                requested_backend=self.vispy_backend,
                available=False,
                context_available=False,
                error=_format_exception(exc),
            )
            self.vispy_diagnostics = diagnostics
            self.vispy_diagnostics_payload = diagnostics.payload()
            self._headless_attempts = []
            self._pending_fallback_reason = diagnostics.fallback_reason
            _log_vispy_diagnostics(diagnostics)
            if force:
                raise
            return None

        self.refresh_vispy_diagnostics(log=True)
        return self._vispy_app

    def use_app(self, backend_name):
        """Force VisPy to use a specific backend."""

        normalized = (
            backend_name.lower() if isinstance(backend_name, str) else backend_name
        )
        self.vispy_backend = normalized
        self._vispy_app = visapp.application.Application(normalized)
        self.refresh_vispy_diagnostics(log=True)
        return self._vispy_app


@dataclass
class _AppContextState:
    """Book-keeping helper for nested application contexts."""

    stack: list[tuple[bool, bool]] = field(default_factory=list)

    def push(self, owned: bool, reset: bool) -> None:
        self.stack.append((owned, reset))

    def pop(self) -> tuple[bool, bool]:
        if not self.stack:
            raise RuntimeError("Application context stack underflow")
        return self.stack.pop()

    def propagate_reset(self, reset: bool) -> None:
        if reset and self.stack:
            owned, parent_reset = self.stack[-1]
            if not parent_reset:
                self.stack[-1] = (owned, True)

    @property
    def depth(self) -> int:
        return len(self.stack)


# Global configuration handle exposed to consumers of :mod:`visbrain.config`.
_SHOW_GUI_ENVVAR = "VISBRAIN_SHOW_GUI"
_BACKGROUND_ENVVAR = "VISBRAIN_BACKGROUND_WORKERS"


def _parse_bool_flag(value: str) -> bool:
    """Return a boolean from a CLI or environment flag value."""

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Unsupported boolean value: {value!r}")


def _read_show_gui_flag(env_value: str) -> bool:
    """Parse an environment toggle for GUI visibility."""

    return _parse_bool_flag(env_value)


def configure_from_environ(
    *,
    environ: Mapping[str, str] | None = None,
    config: VisbrainConfig | None = None,
) -> VisbrainConfig:
    """Update configuration flags from environment variables."""

    env = environ if environ is not None else os.environ
    cfg = config if config is not None else get_config()

    raw_show = env.get(_SHOW_GUI_ENVVAR)
    if raw_show is not None:
        try:
            cfg.show_gui = _read_show_gui_flag(raw_show)
        except ValueError:
            logger.error(
                "Invalid value for %s: %s" % (_SHOW_GUI_ENVVAR, raw_show)
            )

    raw_background = env.get(_BACKGROUND_ENVVAR)
    if raw_background is not None:
        try:
            cfg.background_workers = _parse_bool_flag(raw_background)
        except ValueError:
            logger.error(
                "Invalid value for %s: %s"
                % (_BACKGROUND_ENVVAR, raw_background)
            )
    elif not cfg.show_gui:
        cfg.background_workers = False

    if cfg.show_gui:
        cfg.refresh_vispy_diagnostics(log=True)
    else:
        cfg.apply_headless_backend_policy()

    return cfg


def configure_headless(
    *,
    environ: MutableMapping[str, str] | None = None,
    config: VisbrainConfig | None = None,
    force: bool = False,
) -> VisbrainConfig:
    """Ensure GUI creation is disabled in automated environments.

    Parameters
    ----------
    environ:
        Mapping updated with the headless toggle. Defaults to :data:`os.environ`.
    config:
        Configuration instance to update. Defaults to :func:`get_config()`.
    force:
        When ``True`` the environment toggle is overwritten even if it already
        exists. When ``False`` an existing value takes precedence.
    """

    env = environ if environ is not None else os.environ
    if force or _SHOW_GUI_ENVVAR not in env:
        env[_SHOW_GUI_ENVVAR] = "0"
    if force or _BACKGROUND_ENVVAR not in env:
        env[_BACKGROUND_ENVVAR] = "0"
    return configure_from_environ(environ=env, config=config)


_CONFIG = VisbrainConfig()
_QT_CONTEXT_STATE = _AppContextState()
_VISPY_CONTEXT_STATE = _AppContextState()

configure_from_environ(config=_CONFIG)


def get_config() -> VisbrainConfig:
    """Return the global :class:`VisbrainConfig` instance."""

    return _CONFIG


# Backwards compatible alias
CONFIG = _CONFIG

# Visbrain profiler (derived from the VisPy profiler)
PROFILER = Profiler()


def get_qt_app(
    create: bool = True, *, force: bool = False
) -> Optional[QtWidgets.QApplication]:
    """Return (and optionally create) the Qt application instance."""

    return get_config().get_qt_app(create=create, force=force)


def ensure_qt_app(*, force: bool = False) -> Optional[QtWidgets.QApplication]:
    """Ensure a Qt application exists, respecting the headless flag."""

    return get_config().get_qt_app(create=True, force=force)


def get_vispy_app(
    backend: Optional[str] = None,
    *,
    create: bool = True,
    force: bool = False,
) -> Optional[visapp.Application]:
    """Return (and optionally create) the VisPy application instance."""

    return get_config().get_vispy_app(backend=backend, create=create, force=force)


def ensure_vispy_app(
    backend: Optional[str] = None, *, force: bool = False
) -> Optional[visapp.Application]:
    """Ensure a VisPy application exists, respecting the headless flag."""

    return get_config().get_vispy_app(backend=backend, create=True, force=force)


def use_app(backend_name):
    """Use a specific VisPy backend."""

    return get_config().use_app(backend_name)


def _shutdown_qt_application(
    config: VisbrainConfig, app: QtWidgets.QApplication
) -> None:
    """Attempt to gracefully close a Qt application instance."""

    try:
        quit_method = getattr(app, "quit", None)
        if callable(quit_method):
            quit_method()
        else:
            close_all = getattr(app, "closeAllWindows", None)
            if callable(close_all):  # pragma: no branch - best effort fallback
                close_all()
        delete_later = getattr(app, "deleteLater", None)
        if callable(delete_later):  # pragma: no branch - optional Qt API
            delete_later()
    finally:
        config.pyqt_app = None


def _shutdown_vispy_application(
    config: VisbrainConfig, app: visapp.Application
) -> None:
    """Attempt to gracefully close a VisPy application instance."""

    try:
        quit_method = getattr(app, "quit", None)
        if callable(quit_method):
            quit_method()
    finally:
        config.vispy_app = None


@contextmanager
def qt_app(
    *, create: bool = True, force: bool = False, reset: bool = False
) -> Iterator[Optional[QtWidgets.QApplication]]:
    """Context manager yielding the active Qt application instance."""

    config = get_config()
    previous = config.pyqt_app
    app = config.get_qt_app(create=create, force=force)
    if app is None:
        yield None
        return

    owned = app is not previous
    _QT_CONTEXT_STATE.push(owned, reset)
    try:
        yield app
    finally:
        owned_state, reset_state = _QT_CONTEXT_STATE.pop()
        _QT_CONTEXT_STATE.propagate_reset(reset_state)
        if _QT_CONTEXT_STATE.depth == 0 and (owned_state or reset_state):
            _shutdown_qt_application(config, app)


@contextmanager
def vispy_app(
    backend: Optional[str] = None,
    *,
    create: bool = True,
    force: bool = False,
    reset: bool = False,
    run: bool | Callable[..., Any] | None = None,
) -> Iterator[Optional[visapp.Application]]:
    """Context manager yielding the active VisPy application instance."""

    config = get_config()
    previous = config.vispy_app
    app = config.get_vispy_app(
        backend=backend, create=create, force=force
    )
    if app is None:
        yield None
        return

    owned = app is not previous
    _VISPY_CONTEXT_STATE.push(owned, reset)
    try:
        yield app
        if app is not None and run:
            if callable(run):
                try:
                    run(app)
                except TypeError:
                    run()
            else:
                runner = getattr(app, "run", None)
                if callable(runner):
                    runner()
    finally:
        owned_state, reset_state = _VISPY_CONTEXT_STATE.pop()
        _VISPY_CONTEXT_STATE.propagate_reset(reset_state)
        if _VISPY_CONTEXT_STATE.depth == 0 and (owned_state or reset_state):
            _shutdown_vispy_application(config, app)


# Matplotlib rendering defaults to disabled until explicitly enabled.
get_config().mpl_render = False

# Jupyter / iPython detection enables Matplotlib rendering automatically.
try:  # pragma: no cover - optional dependency
    ip = get_ipython()
except NameError:  # pragma: no cover - IPython not available
    ip = None
else:
    if ip is not None:  # pragma: no branch - executed only in notebooks
        cfg = get_config()
        cfg.mpl_render = True
        import vispy

        vispy.use(cfg.vispy_backend)


VISBRAIN_HELP = """
Visbrain command line arguments:

  --visbrain-log=(profiler|debug|info|warning|error|critical)
    Sets the verbosity of logging output. The default is 'info'.

  --visbrain-search=[search string]
    Search string in logs.

  --visbrain-show=(True|False)
    Control if GUI have to be displayed.

  --visbrain-help
    Display help Visbrain command line help.

"""


def configure_from_argv(
    argv: Sequence[str], *, config: VisbrainConfig | None = None
) -> VisbrainConfig:
    """Parse Visbrain CLI flags from *argv* and return the resulting config."""

    cfg = config if config is not None else get_config()
    argnames = [
        "visbrain-log=",
        "visbrain-show=",
        "visbrain-help",
        "visbrain-search=",
    ]
    try:
        opts, _ = getopt.getopt(list(argv), "", argnames)
    except getopt.GetoptError:
        opts = []

    for option, argument in opts:
        if not option.startswith("--visbrain"):
            continue
        if option == "--visbrain-help":
            print(VISBRAIN_HELP)
            continue
        if option == "--visbrain-log":
            cfg.set_logging(level=argument)
            continue
        if option == "--visbrain-show":
            try:
                cfg.show_gui = _parse_bool_flag(argument)
            except ValueError:
                logger.error(
                    "Invalid value for --visbrain-show: %s" % argument
                )
            else:
                logger.debug("Show GUI resources : %s" % cfg.show_gui)
            continue
        if option == "--visbrain-search":
            cfg.set_logging(match=argument)

    return cfg


def parse_cli(
    argv: Sequence[str], config: VisbrainConfig | None = None
) -> VisbrainConfig:
    """Backward compatible wrapper around :func:`configure_from_argv`."""

    logger.warning(
        "parse_cli is deprecated; call configure_from_argv(...) instead.",
    )
    return configure_from_argv(argv, config=config)


def init_config(argv: Sequence[str]) -> VisbrainConfig:
    """Backward compatible wrapper around :func:`parse_cli`."""

    logger.warning(
        "init_config is deprecated; call parse_cli(...) instead.",
    )
    return parse_cli(argv, CONFIG)

