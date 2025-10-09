"""Tests for :mod:`visbrain.config` initialization helpers."""

from __future__ import annotations

import importlib
import logging
import sys

import pytest

try:
    import vispy.app
except Exception as exc:  # pragma: no cover - exercised on systems without GL
    pytest.skip(
        f"vispy.app unavailable for testing ({exc})", allow_module_level=True
    )

from visbrain import qt as qt_mod


def _reload_config():
    sys.modules.pop("visbrain.config", None)
    return importlib.import_module("visbrain.config")


def test_import_has_no_side_effects(monkeypatch):
    """Importing :mod:`visbrain.config` must not create GUI applications."""

    class DummyQApplication:
        created = 0
        _instance: DummyQApplication | None = None

        @staticmethod
        def instance():
            return DummyQApplication._instance

        @staticmethod
        def setQuitOnLastWindowClosed(enabled):  # pragma: no cover - compatibility
            DummyQApplication._quit_on_last = enabled

        def __init__(self, *args, **kwargs):
            DummyQApplication.created += 1
            DummyQApplication._instance = self

        def processEvents(self):  # pragma: no cover - compatibility
            pass

    class DummyVispyApplication:
        created = 0

        def __init__(self, *args, **kwargs):
            DummyVispyApplication.created += 1

    monkeypatch.setattr(qt_mod.QtWidgets, "QApplication", DummyQApplication)
    monkeypatch.setattr(vispy.app.application, "Application", DummyVispyApplication)

    cfg_mod = _reload_config()
    cfg = cfg_mod.get_config()

    assert DummyQApplication.created == 0
    assert DummyVispyApplication.created == 0
    assert cfg.pyqt_app is None
    assert cfg.vispy_app is None


def _install_dummy_apps(monkeypatch, cfg_mod):
    """Install dummy Qt/VisPy applications and return their classes."""

    class DummyQApplication:
        created = 0
        quitted = 0
        _instance: DummyQApplication | None = None

        @staticmethod
        def instance():
            return DummyQApplication._instance

        @staticmethod
        def setQuitOnLastWindowClosed(enabled):  # pragma: no cover - compatibility
            DummyQApplication._quit_on_last = enabled

        def __init__(self, *args, **kwargs):
            DummyQApplication.created += 1
            DummyQApplication._instance = self
            self.quit_called = 0

        def quit(self):
            DummyQApplication.quitted += 1
            self.quit_called += 1
            DummyQApplication._instance = None

        def deleteLater(self):  # pragma: no cover - exercised in prod only
            pass

        def processEvents(self):  # pragma: no cover - compatibility
            pass

    class DummyVispyApplication:
        created = 0
        quitted = 0

        def __init__(self, backend=None):
            DummyVispyApplication.created += 1
            self.backend = backend
            self.quit_called = 0

        def quit(self):
            DummyVispyApplication.quitted += 1
            self.quit_called += 1

    monkeypatch.setattr(cfg_mod.QtWidgets, "QApplication", DummyQApplication)
    monkeypatch.setattr(
        cfg_mod.visapp.application, "Application", DummyVispyApplication
    )
    return DummyQApplication, DummyVispyApplication


def test_application_context_respects_headless_flag(monkeypatch):
    """Application contexts must honour the ``show_pyqt_app`` toggle."""

    cfg_mod = _reload_config()
    cfg = cfg_mod.get_config()

    DummyQApplication, DummyVispyApplication = _install_dummy_apps(
        monkeypatch, cfg_mod
    )

    cfg.show_pyqt_app = False
    DummyQApplication._instance = None
    DummyQApplication.created = 0
    DummyQApplication.quitted = 0

    with cfg_mod.qt_app() as app:
        assert app is None
    assert DummyQApplication.created == 0
    assert DummyQApplication.quitted == 0

    with cfg_mod.qt_app(force=True) as forced_app:
        assert isinstance(forced_app, DummyQApplication)
        assert forced_app.quit_called == 0
    assert DummyQApplication.created == 1
    assert DummyQApplication.quitted == 1
    assert cfg.pyqt_app is None

    cfg.vispy_app = None
    DummyVispyApplication.created = 0
    DummyVispyApplication.quitted = 0

    with cfg_mod.vispy_app() as app:
        assert app is None
    assert DummyVispyApplication.created == 0
    assert DummyVispyApplication.quitted == 0

    with cfg_mod.vispy_app(force=True) as forced_vispy:
        assert isinstance(forced_vispy, DummyVispyApplication)
        assert forced_vispy.backend == cfg.vispy_backend
        assert forced_vispy.quit_called == 0
    assert DummyVispyApplication.created == 1
    assert DummyVispyApplication.quitted == 1
    assert cfg.vispy_app is None


def test_application_context_nested_teardown(monkeypatch):
    """Nested contexts should reuse instances and close them once."""

    cfg_mod = _reload_config()
    cfg = cfg_mod.get_config()

    DummyQApplication, DummyVispyApplication = _install_dummy_apps(
        monkeypatch, cfg_mod
    )

    cfg.show_pyqt_app = True
    DummyQApplication.created = 0
    DummyQApplication.quitted = 0

    with cfg_mod.qt_app(force=True) as outer_app:
        assert isinstance(outer_app, DummyQApplication)
        assert DummyQApplication.created == 1
        assert cfg.pyqt_app is outer_app
        with cfg_mod.qt_app() as inner_app:
            assert inner_app is outer_app
        assert DummyQApplication.quitted == 0
    assert DummyQApplication.quitted == 1
    assert cfg.pyqt_app is None

    DummyVispyApplication.created = 0
    DummyVispyApplication.quitted = 0

    with cfg_mod.vispy_app(force=True) as outer_vispy:
        assert isinstance(outer_vispy, DummyVispyApplication)
        assert DummyVispyApplication.created == 1
        assert cfg.vispy_app is outer_vispy
        with cfg_mod.vispy_app() as inner_vispy:
            assert inner_vispy is outer_vispy
        assert DummyVispyApplication.quitted == 0
    assert DummyVispyApplication.quitted == 1
    assert cfg.vispy_app is None


def test_application_context_explicit_reset(monkeypatch):
    """Contexts should be able to reset pre-existing application handles."""

    cfg_mod = _reload_config()
    cfg = cfg_mod.get_config()

    DummyQApplication, DummyVispyApplication = _install_dummy_apps(
        monkeypatch, cfg_mod
    )

    cfg.show_pyqt_app = True
    DummyQApplication.created = 0
    DummyQApplication.quitted = 0
    existing_qapp = DummyQApplication()
    DummyQApplication.created = 0
    cfg.pyqt_app = existing_qapp

    with cfg_mod.qt_app(create=False) as app:
        assert app is existing_qapp
    assert DummyQApplication.created == 0
    assert DummyQApplication.quitted == 0
    assert cfg.pyqt_app is existing_qapp

    with cfg_mod.qt_app(create=False, reset=True) as app:
        assert app is existing_qapp
    assert DummyQApplication.quitted == 1
    assert cfg.pyqt_app is None

    DummyVispyApplication.created = 0
    DummyVispyApplication.quitted = 0
    existing_vispy = DummyVispyApplication(cfg.vispy_backend)
    DummyVispyApplication.created = 0
    cfg.vispy_app = existing_vispy

    with cfg_mod.vispy_app(create=False) as app:
        assert app is existing_vispy
    assert DummyVispyApplication.created == 0
    assert DummyVispyApplication.quitted == 0
    assert cfg.vispy_app is existing_vispy

    with cfg_mod.vispy_app(create=False, reset=True) as app:
        assert app is existing_vispy
    assert DummyVispyApplication.quitted == 1
    assert cfg.vispy_app is None


def test_configure_from_argv_updates_runtime(monkeypatch, caplog):
    """CLI parsing should rely solely on the provided ``argv`` sequence."""

    cfg_mod = _reload_config()
    cfg = cfg_mod.get_config()

    baseline = cfg.copy()

    # Pretend the runtime was invoked with a conflicting flag and ensure it is
    # ignored when ``argv`` is empty.
    monkeypatch.setattr(sys, "argv", ["visbrain", "--visbrain-show=False"])
    untouched = cfg_mod.configure_from_argv([], config=baseline.copy())
    assert untouched.show_pyqt_app is baseline.show_pyqt_app

    # Parsing explicit arguments must update the provided config in place and
    # apply logging preferences.
    mutated = baseline.copy()
    caplog.set_level(logging.DEBUG, logger="visbrain")
    result = cfg_mod.configure_from_argv(
        ["--visbrain-show=False", "--visbrain-log=debug", "--visbrain-search=test"],
        config=mutated,
    )
    assert result is mutated
    assert mutated.show_gui is False
    assert mutated.log_level == "debug"
    assert mutated.log_search == "test"

    # Invalid boolean values should log an error and leave the flag unchanged.
    error_target = baseline.copy()
    cfg_mod.configure_from_argv(["--visbrain-show=not-a-bool"], config=error_target)
    assert error_target.show_pyqt_app is baseline.show_pyqt_app
    assert any(
        "Invalid value for --visbrain-show" in rec.message
        for rec in caplog.records
    )

    # Calling without an explicit config should mutate the shared singleton.
    cfg.show_gui = True
    cfg_mod.configure_from_argv(["--visbrain-show=False"])
    assert cfg.show_gui is False


def test_environment_overrides_default(monkeypatch):
    """Environment variables should control the headless toggle."""

    monkeypatch.setenv("VISBRAIN_SHOW_GUI", "0")
    cfg_mod = _reload_config()
    cfg = cfg_mod.get_config()
    assert cfg.show_gui is False

    monkeypatch.setenv("VISBRAIN_SHOW_GUI", "1")
    cfg_mod = _reload_config()
    cfg = cfg_mod.get_config()
    assert cfg.show_gui is True


def test_configure_headless_defaults():
    """The helper should set the environment default when unset."""

    cfg_mod = _reload_config()
    env: dict[str, str] = {}
    config = cfg_mod.VisbrainConfig()

    result = cfg_mod.configure_headless(environ=env, config=config)
    assert env["VISBRAIN_SHOW_GUI"] == "0"
    assert result.show_gui is False


def test_configure_headless_respects_existing():
    """Existing environment toggles should be honoured by default."""

    cfg_mod = _reload_config()
    env = {"VISBRAIN_SHOW_GUI": "1"}
    config = cfg_mod.VisbrainConfig()

    result = cfg_mod.configure_headless(environ=env, config=config)
    assert env["VISBRAIN_SHOW_GUI"] == "1"
    assert result.show_gui is True

    forced = cfg_mod.configure_headless(
        environ=env, config=config, force=True
    )
    assert env["VISBRAIN_SHOW_GUI"] == "0"
    assert forced.show_gui is False


def test_configure_from_environ_invalid_value(caplog):
    """Invalid environment toggles should log an error and be ignored."""

    cfg_mod = _reload_config()
    env = {"VISBRAIN_SHOW_GUI": "maybe"}
    config = cfg_mod.VisbrainConfig()

    caplog.set_level(logging.ERROR, logger="visbrain")
    cfg_mod.configure_from_environ(environ=env, config=config)

    assert config.show_gui is True
    assert any(
        "Invalid value for VISBRAIN_SHOW_GUI" in record.message
        for record in caplog.records
    )


def test_config_copy_preserves_diagnostics_payload():
    """Copies should keep the full diagnostics snapshot and payload."""

    cfg_mod = _reload_config()
    base = cfg_mod.VisbrainConfig()
    base.vispy_diagnostics = cfg_mod.VisPyDiagnostics(
        requested_backend="egl",
        resolved_backend="egl",
        available=True,
        context_available=True,
        fallback_reason="Configured headless backend 'egl'",
        headless_attempts=[{"backend": "egl", "success": True}],
        shader_compiled=True,
    )
    base.vispy_diagnostics_payload = base.vispy_diagnostics.payload()
    base._headless_attempts = [
        {"backend": "egl", "success": True}
    ]
    base._pending_fallback_reason = base.vispy_diagnostics.fallback_reason

    clone = base.copy()

    assert (
        clone.vispy_diagnostics.fallback_reason
        == base.vispy_diagnostics.fallback_reason
    )
    assert clone.vispy_diagnostics.headless_attempts[0]["backend"] == "egl"
    assert clone.vispy_diagnostics_payload["shader_compiled"] is True
