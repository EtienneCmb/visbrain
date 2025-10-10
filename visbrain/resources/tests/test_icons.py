"""Tests for :mod:`visbrain.resources.icons`."""
from __future__ import annotations

import logging
import sys
import types
from importlib import import_module

import pytest


class _FakeQByteArray(bytearray):
    """Minimal ``QByteArray`` stand-in preserving payload bytes."""

    def __new__(cls, data: bytes):
        return super().__new__(cls, data)


class _FakeQSize:
    """Small helper mimicking :class:`QtCore.QSize`."""

    def __init__(self, width: int = 0, height: int = 0) -> None:
        self._width = width
        self._height = height

    def isValid(self) -> bool:  # pragma: no cover - trivial
        return self._width > 0 and self._height > 0


class _FakeQImage:
    """In-memory ``QImage`` replacement used for rendering."""

    Format_ARGB32 = object()

    def __init__(self, size: _FakeQSize, _format: object) -> None:
        self.size = size
        self.format = _format
        self.filled = False

    def fill(self, value: int) -> None:  # pragma: no cover - trivial
        self.filled = True


class _FakeQPixmap:
    """``QPixmap`` stub supporting ``loadFromData`` and ``fromImage``."""

    def __init__(self) -> None:
        self.loaded_payload: bytes | None = None
        self.from_image: _FakeQImage | None = None

    def loadFromData(self, data: bytes) -> bool:  # pragma: no cover - patched in tests
        self.loaded_payload = data
        return True

    @staticmethod
    def fromImage(image: _FakeQImage) -> "_FakeQPixmap":
        pixmap = _FakeQPixmap()
        pixmap.from_image = image
        return pixmap


class _FakeQIcon:
    """Simple container holding the ``QPixmap`` provided to it."""

    def __init__(self, pixmap: _FakeQPixmap) -> None:
        self.pixmap = pixmap


class _FakeQPainter:
    """Minimal :class:`QtGui.QPainter` stand-in."""

    def __init__(self, image: _FakeQImage) -> None:
        self.image = image
        self.ended = False

    def end(self) -> None:  # pragma: no cover - trivial
        self.ended = True


class _FakeQSvgRenderer:
    """SVG renderer returning a predictable size and signalling success."""

    def __init__(self, payload: _FakeQByteArray) -> None:
        self.payload = payload
        self._valid = True

    def isValid(self) -> bool:  # pragma: no cover - defensive
        return self._valid

    def defaultSize(self) -> _FakeQSize:  # pragma: no cover - trivial
        return _FakeQSize(48, 48)

    def render(self, painter: _FakeQPainter) -> None:  # pragma: no cover - trivial
        painter.rendered_payload = bytes(self.payload)


_fake_qt_core = types.SimpleNamespace(QByteArray=_FakeQByteArray, QSize=_FakeQSize)
_fake_qt_gui = types.SimpleNamespace(
    QImage=_FakeQImage,
    QPixmap=_FakeQPixmap,
    QIcon=_FakeQIcon,
    QPainter=_FakeQPainter,
)
_fake_qt = types.SimpleNamespace(QSvgRenderer=_FakeQSvgRenderer)

_fake_qt_module = types.ModuleType("visbrain.qt")
_fake_qt_module.QtCore = _fake_qt_core
_fake_qt_module.QtGui = _fake_qt_gui
_fake_qt_module.QtWidgets = types.SimpleNamespace()
_fake_qt_module.Qt = _fake_qt
_fake_qt_module.QT_API = "stub"
_fake_qt_module.guard_qapp_lifecycle = lambda: None

sys.modules.setdefault("visbrain.qt", _fake_qt_module)

icons = import_module("visbrain.resources.icons._impl")

SVG_PAYLOAD = b"<svg xmlns='http://www.w3.org/2000/svg'></svg>"


def test_render_svg_icon_uses_svg_renderer(monkeypatch: pytest.MonkeyPatch) -> None:
    """``_render_svg_icon`` should return a ``QIcon`` when QtSvg is present."""

    monkeypatch.setattr(
        icons.QtGui.QPixmap,
        "loadFromData",
        lambda self, data: False,
        raising=False,
    )
    icon = icons._render_svg_icon(SVG_PAYLOAD)
    assert isinstance(icon, icons.QtGui.QIcon)
    assert isinstance(icon.pixmap, icons.QtGui.QPixmap)
    assert isinstance(icon.pixmap.from_image, icons.QtGui.QImage)


def test_render_svg_icon_without_svg_renderer(monkeypatch: pytest.MonkeyPatch) -> None:
    """When ``Qt.QSvgRenderer`` is unavailable the fallback returns ``None``."""

    monkeypatch.setattr(icons, "Qt", types.SimpleNamespace(), raising=False)
    monkeypatch.setattr(
        icons.QtGui.QPixmap,
        "loadFromData",
        lambda self, data: False,
        raising=False,
    )
    assert icons._render_svg_icon(SVG_PAYLOAD) is None


class _FakeResourcePath:
    """Small stand-in mimicking ``importlib.resources`` path objects."""

    def __init__(
        self,
        *,
        exists: bool,
        data: bytes | None,
        error: Exception | None,
    ) -> None:
        self._exists = exists
        self._data = data
        self._error = error

    def is_file(self) -> bool:
        return self._exists

    def read_bytes(self) -> bytes:
        if self._error is not None:
            raise self._error
        if self._data is None:
            raise FileNotFoundError("no data available")
        return self._data


class _FakeResourceRoot:
    """Return the fake path object regardless of the requested name."""

    def __init__(self, path: _FakeResourcePath) -> None:
        self._path = path

    def joinpath(
        self,
        icon_name: str,
    ) -> _FakeResourcePath:  # pragma: no cover - trivial
        self._path.requested = icon_name
        return self._path


@pytest.fixture
def missing_icon_resource(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub :func:`resources.files` with a path reporting ``is_file`` as ``False``."""

    path = _FakeResourcePath(exists=False, data=None, error=None)
    root = _FakeResourceRoot(path)
    monkeypatch.setattr(icons.resources, "files", lambda _pkg: root)


@pytest.fixture
def zip_error_resource(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub :func:`resources.files` with a path raising :class:`FileNotFoundError`."""

    path = _FakeResourcePath(exists=True, data=None, error=FileNotFoundError("zip"))
    root = _FakeResourceRoot(path)
    monkeypatch.setattr(icons.resources, "files", lambda _pkg: root)


def test_load_icon_logs_when_missing(
    caplog: pytest.LogCaptureFixture,
    missing_icon_resource: None,
) -> None:
    """Missing icon files should be logged and return ``None``."""

    caplog.set_level(logging.DEBUG, logger="visbrain")
    assert icons.load_icon("absent.svg") is None
    assert "No icon found (absent.svg)" in caplog.text


def test_load_icon_logs_zip_error(
    caplog: pytest.LogCaptureFixture,
    zip_error_resource: None,
) -> None:
    """Zip importer failures should be logged and return ``None``."""

    caplog.set_level(logging.DEBUG, logger="visbrain")
    assert icons.load_icon("archived.svg") is None
    assert "Unable to access icon resource (archived.svg)" in caplog.text
