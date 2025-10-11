"""Tests for VisPy/OpenGL diagnostics and fallback behaviour."""

from __future__ import annotations

import json
import importlib
import logging
import sys
import types

import pytest

def _reload_config():
    sys.modules.pop("visbrain.config", None)
    return importlib.import_module("visbrain.config")


def _clear_vispy_modules():
    for name in list(sys.modules):
        if name == "vispy" or name.startswith("vispy."):
            sys.modules.pop(name, None)


def _install_runtime_stubs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Install lightweight stubs for utility and Qt dependencies."""

    logging_mod = types.ModuleType("visbrain.utils.logging")
    logging_mod.set_log_level = lambda level, match=None: None

    others_mod = types.ModuleType("visbrain.utils.others")

    class DummyProfiler:
        def __call__(self, *args, **kwargs):  # pragma: no cover - compatibility
            return None

    others_mod.Profiler = DummyProfiler

    utils_pkg = types.ModuleType("visbrain.utils")
    utils_pkg.__path__ = []  # Mark as package for submodule imports

    monkeypatch.setitem(sys.modules, "visbrain.utils", utils_pkg)
    monkeypatch.setitem(sys.modules, "visbrain.utils.logging", logging_mod)
    monkeypatch.setitem(sys.modules, "visbrain.utils.others", others_mod)

    class _DummySignal:
        def connect(self, *_args, **_kwargs):  # pragma: no cover - compatibility
            return None

    class DummyQObject:
        destroyed = _DummySignal()

    class DummyQCoreApplication:
        @staticmethod
        def closingDown() -> bool:
            return False

    class DummyQApplication:
        _instance: "DummyQApplication | None" = None

        def __init__(self, *_args, **_kwargs):
            DummyQApplication._instance = self

        @staticmethod
        def instance() -> "DummyQApplication | None":
            return DummyQApplication._instance

        @staticmethod
        def setQuitOnLastWindowClosed(_flag: bool) -> None:
            return None

        def quit(self) -> None:  # pragma: no cover - compatibility
            return None

        def deleteLater(self) -> None:  # pragma: no cover - compatibility
            return None

    dummy_qt = types.ModuleType("visbrain.qt")
    dummy_qt.QT_API = "stub"
    dummy_qt.QtCore = types.SimpleNamespace(
        QCoreApplication=DummyQCoreApplication, QObject=DummyQObject
    )
    dummy_qt.QtWidgets = types.SimpleNamespace(QApplication=DummyQApplication)
    dummy_qt.guard_qapp_lifecycle = lambda: None

    monkeypatch.setitem(sys.modules, "visbrain.qt", dummy_qt)


def test_vispy_import_failure_emits_warning(monkeypatch, caplog, recwarn):
    """Import errors from :mod:`vispy.app` should surface as warnings."""

    _clear_vispy_modules()
    _install_runtime_stubs(monkeypatch)
    real_import_module = importlib.import_module

    def fake_import(name, *args, **kwargs):
        if name == "vispy.app":
            raise OSError("GL implementation missing")
        return real_import_module(name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    caplog.set_level(logging.INFO, logger="visbrain")

    cfg_mod = _reload_config()
    cfg = cfg_mod.get_config()

    assert cfg.vispy_diagnostics.available is False
    assert cfg.vispy_diagnostics.context_available is False
    assert "GL implementation missing" in (cfg.vispy_diagnostics.error or "")
    assert cfg.vispy_diagnostics.shader_compiled is None
    assert cfg.vispy_diagnostics_payload["error"].startswith("OSError")
    assert cfg.vispy_diagnostics_payload.get("headless_attempts") in (None, [])
    assert any("vispy.probe" in record.message for record in caplog.records)
    assert any(
        "VisPy backend unavailable" in str(w.message) for w in recwarn.list
    )


def test_headless_backend_fallback_prefers_egl(monkeypatch, caplog, recwarn):
    """Headless startup should configure an offscreen backend when available."""

    _clear_vispy_modules()
    _install_runtime_stubs(monkeypatch)
    monkeypatch.setenv("VISBRAIN_SHOW_GUI", "0")

    class DummyConfig(dict):
        def __getitem__(self, key):
            return super().get(key, "")

        def __setitem__(self, key, value):
            super().__setitem__(key, value)

    attempts: list[str] = []

    class DummyApplication:
        def __init__(self, backend=None):
            backend_name = (backend or "egl").lower()
            attempts.append(backend_name)
            if backend_name != "egl":
                raise RuntimeError(f"Backend {backend_name} unavailable")
            self._backend = backend_name

        @property
        def backend_name(self):
            return self._backend

    class DummyGLInfo:
        have_context = True

        def get_version(self):
            return "4.5 Dummy"

        def get_renderer(self):
            return "DummyGPU"

    def _get_int(constant):
        limits = {
            "GL_MAX_TEXTURE_SIZE": 8192,
            "GL_MAX_3D_TEXTURE_SIZE": 4096,
            "GL_MAX_TEXTURE_IMAGE_UNITS": 16,
        }
        return limits.get(constant, 0)

    class DummyProgram:
        def __init__(self, *args, **kwargs):
            self._built = False

        def _build(self):
            self._built = True

        def delete(self):
            return None

    dummy_config = DummyConfig()
    dummy_app = types.ModuleType("vispy.app")
    dummy_app.application = types.SimpleNamespace(Application=DummyApplication)
    dummy_app.use_app = lambda backend=None: DummyApplication(backend)

    dummy_vispy = types.ModuleType("vispy")
    dummy_vispy.config = dummy_config

    dummy_gl = types.SimpleNamespace(
        gl_info=DummyGLInfo(),
        GL_MAX_TEXTURE_SIZE="GL_MAX_TEXTURE_SIZE",
        GL_MAX_3D_TEXTURE_SIZE="GL_MAX_3D_TEXTURE_SIZE",
        GL_MAX_TEXTURE_IMAGE_UNITS="GL_MAX_TEXTURE_IMAGE_UNITS",
        glGetIntegerv=_get_int,
    )
    dummy_gloo = types.SimpleNamespace(gl=dummy_gl, Program=DummyProgram)

    monkeypatch.setitem(sys.modules, "vispy", dummy_vispy)
    monkeypatch.setitem(sys.modules, "vispy.app", dummy_app)
    monkeypatch.setitem(sys.modules, "vispy.gloo", dummy_gloo)
    monkeypatch.setitem(sys.modules, "vispy.gloo.gl", dummy_gl)

    caplog.set_level(logging.INFO, logger="visbrain")

    cfg_mod = _reload_config()
    cfg = cfg_mod.get_config()

    assert cfg.show_gui is False
    assert cfg.vispy_backend == "egl"
    assert dummy_config["default_backend"] == "egl"
    assert cfg.vispy_diagnostics.available is True
    assert cfg.vispy_diagnostics.context_available is True
    assert cfg.vispy_diagnostics.gl_version == "4.5 Dummy"
    assert cfg.vispy_diagnostics.renderer == "DummyGPU"
    assert cfg.vispy_diagnostics.max_texture_size == 8192
    assert cfg.vispy_diagnostics.max_texture_3d_size == 4096
    assert cfg.vispy_diagnostics.max_texture_units == 16
    assert cfg.vispy_diagnostics.shader_compiled is True
    assert cfg.vispy_diagnostics.shader_error is None
    assert (
        cfg.vispy_diagnostics.fallback_reason
        == "Configured headless backend 'egl'"
    )
    assert cfg.vispy_diagnostics.headless_attempts == [
        {"backend": "egl", "success": True}
    ]
    assert cfg.vispy_diagnostics_payload["max_texture_size"] == 8192
    assert cfg.vispy_diagnostics_payload["shader_compiled"] is True
    assert cfg.vispy_diagnostics_payload["fallback_reason"].startswith(
        "Configured headless backend"
    )
    assert cfg.vispy_diagnostics_payload["headless_attempts"][0]["backend"] == "egl"
    assert "egl" in attempts
    assert any("vispy.headless" in record.message for record in caplog.records)
    assert any("vispy.probe" in record.message for record in caplog.records)
    assert not recwarn.list


def test_missing_gl_info_reports_context_unavailable(monkeypatch, recwarn):
    """Missing :mod:`vispy.gloo.gl.gl_info` should not crash diagnostics."""

    _clear_vispy_modules()
    _install_runtime_stubs(monkeypatch)

    class DummyApplication:
        backend_name = "pyside6"

        def __init__(self, *_args, **_kwargs):
            return None

    dummy_app = types.ModuleType("vispy.app")
    dummy_app.application = types.SimpleNamespace(Application=DummyApplication)
    dummy_app.use_app = lambda backend=None: DummyApplication()

    dummy_vispy = types.ModuleType("vispy")
    dummy_vispy.config = {}

    dummy_gl = types.SimpleNamespace(
        GL_MAX_TEXTURE_SIZE="GL_MAX_TEXTURE_SIZE",
        GL_MAX_3D_TEXTURE_SIZE="GL_MAX_3D_TEXTURE_SIZE",
        GL_MAX_TEXTURE_IMAGE_UNITS="GL_MAX_TEXTURE_IMAGE_UNITS",
        glGetIntegerv=lambda *_args, **_kwargs: 0,
    )
    dummy_gloo = types.SimpleNamespace(gl=dummy_gl)

    monkeypatch.setitem(sys.modules, "vispy", dummy_vispy)
    monkeypatch.setitem(sys.modules, "vispy.app", dummy_app)
    monkeypatch.setitem(sys.modules, "vispy.gloo", dummy_gloo)
    monkeypatch.setitem(sys.modules, "vispy.gloo.gl", dummy_gl)

    cfg_mod = _reload_config()
    cfg = cfg_mod.get_config()

    assert cfg.vispy_diagnostics.available is True
    assert cfg.vispy_diagnostics.context_available is False
    assert cfg.vispy_diagnostics.error == (
        "OpenGL capability probe unavailable: vispy.gloo.gl.gl_info missing"
    )
    assert cfg.vispy_diagnostics.shader_compiled is None
    assert cfg.vispy_diagnostics_payload["error"].startswith("OpenGL capability")
    assert cfg.vispy_diagnostics_payload.get("fallback_reason") is None
    assert cfg.vispy_diagnostics_payload.get("headless_attempts") in (None, [])
    assert any(
        "VisPy backend unavailable" in str(w.message)
        for w in recwarn.list
    )


def test_headless_backend_failure_reports_attempts(monkeypatch, caplog, recwarn):
    """Structured logging should record failed headless attempts."""

    _clear_vispy_modules()
    _install_runtime_stubs(monkeypatch)
    monkeypatch.setenv("VISBRAIN_SHOW_GUI", "0")

    class DummyApplication:
        def __init__(self, backend=None):
            raise RuntimeError(f"{backend} backend missing")

    dummy_app = types.ModuleType("vispy.app")
    dummy_app.application = types.SimpleNamespace(Application=DummyApplication)
    dummy_app.use_app = lambda backend=None: (_ for _ in ()).throw(
        RuntimeError("no backends")
    )

    dummy_vispy = types.ModuleType("vispy")
    dummy_vispy.config = {}

    dummy_gloo = types.SimpleNamespace(gl=types.SimpleNamespace())

    monkeypatch.setitem(sys.modules, "vispy", dummy_vispy)
    monkeypatch.setitem(sys.modules, "vispy.app", dummy_app)
    monkeypatch.setitem(sys.modules, "vispy.gloo", dummy_gloo)
    monkeypatch.setitem(sys.modules, "vispy.gloo.gl", dummy_gloo.gl)

    caplog.set_level(logging.INFO, logger="visbrain")

    cfg_mod = _reload_config()
    cfg = cfg_mod.get_config()

    assert cfg.vispy_diagnostics.available is False
    assert cfg.vispy_diagnostics.fallback_reason.startswith(
        "No suitable headless VisPy backend"
    )
    attempts = cfg.vispy_diagnostics.headless_attempts
    assert len(attempts) == 2
    assert {attempt["backend"] for attempt in attempts} == {"egl", "osmesa"}
    assert all(attempt["success"] is False for attempt in attempts)
    assert cfg.vispy_diagnostics_payload["fallback_reason"].startswith(
        "No suitable headless"
    )
    assert any("vispy.headless" in record.message for record in caplog.records)
    assert any(
        "No suitable headless" in str(w.message) for w in recwarn.list
    )


def test_cli_info_text_output(monkeypatch, capsys):
    """The CLI should render human readable diagnostics and guidance."""

    main_mod = importlib.import_module("visbrain.__main__")

    payload = {
        "available": True,
        "context_available": True,
        "requested_backend": "egl",
        "resolved_backend": "egl",
        "shader_compiled": True,
        "fallback_reason": "Configured headless backend 'egl'",
        "headless_attempts": [{"backend": "egl", "success": True}],
    }

    diag = types.SimpleNamespace(payload=lambda: payload)

    class DummyConfig:
        def __init__(self):
            self.vispy_diagnostics = diag
            self.vispy_diagnostics_payload = dict(payload)

        def refresh_vispy_diagnostics(self, log=True):
            return self.vispy_diagnostics

    monkeypatch.setattr(main_mod, "get_config", lambda: DummyConfig())

    code = main_mod.main(["info"])
    captured = capsys.readouterr()
    assert code == 0
    assert "Visbrain OpenGL diagnostics" in captured.out
    assert "Guidance:" in captured.out
    assert "Headless rendering active" in captured.out


def test_cli_info_json_output_reports_failure(monkeypatch, capsys):
    """JSON output should contain the diagnostics payload verbatim."""

    main_mod = importlib.import_module("visbrain.__main__")

    payload = {
        "available": False,
        "context_available": False,
        "error": "OSError: Missing GL",
    }

    diag = types.SimpleNamespace(payload=lambda: payload)

    class DummyConfig:
        def __init__(self):
            self.vispy_diagnostics = diag
            self.vispy_diagnostics_payload = dict(payload)

        def refresh_vispy_diagnostics(self, log=True):
            return self.vispy_diagnostics

    monkeypatch.setattr(main_mod, "get_config", lambda: DummyConfig())

    code = main_mod.main(["info", "--json"])
    captured = capsys.readouterr()
    assert code == 0
    data = json.loads(captured.out)
    assert data["available"] is False
    assert data["error"] == "OSError: Missing GL"
