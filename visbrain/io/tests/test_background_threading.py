"""Tests for the :mod:`visbrain.io.background` helpers."""

from __future__ import annotations

import logging

from visbrain.io import background


def test_call_on_main_thread_without_qt(monkeypatch, caplog):
    """Fallback to inline execution when Qt bindings are unavailable."""

    monkeypatch.setattr(background, "QtCore", None)
    monkeypatch.setattr(background, "QtWidgets", None)

    calls = []

    def sample(value):
        calls.append(value)
        return value * 2

    with caplog.at_level(logging.DEBUG, logger="visbrain"):
        result = background.call_on_main_thread(sample, 21)

    assert result == 42
    assert calls == [21]
    assert any(
        "Qt bindings unavailable" in record.getMessage() for record in caplog.records
    )
