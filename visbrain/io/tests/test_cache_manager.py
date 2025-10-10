"""Tests for :mod:`visbrain.io.cache` and cache-backed path helpers."""
from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest

if "visbrain.qt" not in sys.modules:
    qt_stub = types.ModuleType("visbrain.qt")
    qt_stub.QtWidgets = types.SimpleNamespace(
        QFileDialog=types.SimpleNamespace(
            getSaveFileName=lambda *args, **kwargs: ("", ""),
            getOpenFileName=lambda *args, **kwargs: ("", ""),
        ),
        QColorDialog=types.SimpleNamespace(
            getColor=lambda *args, **kwargs: types.SimpleNamespace(name=lambda: "")
        ),
        QApplication=types.SimpleNamespace(instance=lambda: None),
    )
    qt_stub.QtCore = types.SimpleNamespace(
        QThread=types.SimpleNamespace(currentThread=lambda: None)
    )
    qt_stub.QtGui = types.SimpleNamespace()
    sys.modules["visbrain.qt"] = qt_stub

import visbrain as _visbrain_pkg

_IO_ROOT = Path(__file__).resolve().parent.parent

if "visbrain.io" not in sys.modules:
    io_module = types.ModuleType("visbrain.io")
    io_module.__path__ = [str(_IO_ROOT)]
    sys.modules["visbrain.io"] = io_module
    setattr(_visbrain_pkg, "io", io_module)

cache_module = importlib.import_module("visbrain.io.cache")
path_module = importlib.import_module("visbrain.io.path")
CacheManager = cache_module.CacheManager


@pytest.fixture
def cache_env(tmp_path):
    """Return an isolated manager and its base directory."""

    def factory(name: str):
        return lambda create: tmp_path / name

    manager = CacheManager(
        {
            "tmp": factory("tmp"),
            "data": factory("data"),
        },
        default_category="tmp",
    )
    return manager, tmp_path


def test_get_path_and_cleanup_owner(cache_env):
    """Paths are created per-category and tied to their owners."""

    manager, base = cache_env

    tmp_folder = manager.get_path(folder=("alpha",), create=True, owner="alice")
    data_file = manager.get_path(
        folder="beta",
        file="payload.txt",
        create=True,
        category="data",
        owner="bob",
    )

    assert tmp_folder == base / "tmp" / "alpha"
    assert tmp_folder.is_dir()
    assert data_file == base / "data" / "beta" / "payload.txt"
    assert data_file.is_file()

    manager.cleanup_owner("alice")
    assert not tmp_folder.exists()
    assert data_file.exists()

    manager.cleanup_owner("bob")
    assert not data_file.exists()


def test_new_session_creates_unique_directories(cache_env):
    """``new_session`` yields unique directories registered to the owner."""

    manager, base = cache_env

    first = manager.new_session("owner", prefix="sessions")
    second = manager.new_session("owner", prefix="sessions")

    assert first.parent == base / "tmp" / "sessions"
    assert second.parent == first.parent
    assert first != second
    assert first.exists()
    assert second.exists()

    manager.cleanup_owner("owner")
    assert not first.exists()
    assert not second.exists()


def test_cleanup_all_and_root_path(cache_env):
    """Category-wide cleanup removes registered paths and the root tree."""

    manager, base = cache_env

    tmp_root = manager.root_path()
    data_root = manager.root_path(category="data")
    assert tmp_root == base / "tmp"
    assert data_root == base / "data"
    assert not tmp_root.exists()
    assert not data_root.exists()

    owned_dir = manager.get_path(folder="ephemeral", create=True, owner="eve")
    data_owned = manager.get_path(
        folder="persistent",
        create=True,
        category="data",
        owner="dave",
    )
    assert owned_dir.exists()
    assert data_owned.exists()

    manager.cleanup_all(category="data")
    assert not data_owned.exists()
    assert not data_root.exists()
    assert owned_dir.exists()
    assert "dave" not in manager._owners  # type: ignore[attr-defined]

    manager.cleanup_all()
    assert not owned_dir.exists()
    assert not tmp_root.exists()
    assert "eve" not in manager._owners  # type: ignore[attr-defined]


def _reset_cache_environment(monkeypatch: pytest.MonkeyPatch, base: Path) -> None:
    """Point the global cache manager at *base* and clear any remnants."""

    monkeypatch.setenv("VISBRAIN_DATA_DIR", str(base))
    path_module.cache_manager.cleanup_all()
    path_module.cache_manager.cleanup_all(category="data")


def test_path_to_visbrain_data_prefers_bundled(monkeypatch, tmp_path):
    """Bundled resources are returned without touching writable storage."""

    base = tmp_path / "data_home"
    _reset_cache_environment(monkeypatch, base)

    bundled_file = tmp_path / "bundle" / "roi" / "atlas.npz"
    bundled_file.parent.mkdir(parents=True, exist_ok=True)
    bundled_file.write_text("bundled")

    def fake_bundled_path(*parts):
        if parts == ("roi", "atlas.npz"):
            return bundled_file
        raise FileNotFoundError

    monkeypatch.setattr(path_module, "bundled_path", fake_bundled_path)

    result = path_module.path_to_visbrain_data(file="atlas.npz", folder="roi")
    assert result == str(bundled_file)
    assert not base.exists()


def test_path_to_visbrain_data_honors_env_override(monkeypatch, tmp_path):
    """``VISBRAIN_DATA_DIR`` determines where writable data lives."""

    override = tmp_path / "custom_home"
    _reset_cache_environment(monkeypatch, override)

    folder_path = path_module.path_to_visbrain_data(
        folder="datasets", create=True, allow_bundled=False
    )
    assert Path(folder_path) == override / "datasets"
    assert Path(folder_path).exists()


def test_path_to_visbrain_data_create_file(monkeypatch, tmp_path):
    """``create=True`` touches requested files inside the data cache."""

    data_home = tmp_path / "create_home"
    _reset_cache_environment(monkeypatch, data_home)

    file_path = path_module.path_to_visbrain_data(
        folder="samples",
        file="example.txt",
        create=True,
        allow_bundled=False,
    )
    target = Path(file_path)
    assert target.exists()
    assert target.is_file()
    assert target.parent == data_home / "samples"
