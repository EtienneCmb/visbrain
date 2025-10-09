"""Unit tests for the background loader helpers."""

from __future__ import annotations

import threading

import numpy as np
import pytest

from visbrain.io.background import (
    call_on_main_thread,
    run_in_loader_thread,
    shutdown_loader_threads,
)
import visbrain.io.background as background_mod
from visbrain.io.read_sleep import ReadSleepData


@pytest.fixture(autouse=True)
def cleanup_executor():
    """Ensure loader threads are stopped between tests."""

    yield
    shutdown_loader_threads(wait=True)


def test_run_in_loader_thread_success():
    """Background execution returns the function result."""

    future = run_in_loader_thread(lambda value: value + 1, 41)
    assert future.result(timeout=2) == 42


def test_run_in_loader_thread_propagates_errors():
    """Exceptions raised in the worker thread surface via the future."""

    def boom() -> None:
        raise RuntimeError("kaboom")

    future = run_in_loader_thread(boom)
    with pytest.raises(RuntimeError):
        future.result(timeout=2)


def test_run_in_loader_thread_cancellation():
    """Tasks queued behind a blocking job can be cancelled."""

    started = threading.Event()
    release = threading.Event()

    def blocker() -> None:
        started.set()
        release.wait(timeout=2)

    blocking_future = run_in_loader_thread(blocker)
    started.wait(timeout=2)

    pending_future = run_in_loader_thread(lambda: "unused")
    assert pending_future.cancel()
    assert pending_future.cancelled()

    release.set()
    assert blocking_future.result(timeout=2) is None


def test_call_on_main_thread_without_qt():
    """When Qt is unavailable the callable executes immediately."""

    result = call_on_main_thread(lambda x: x * 2, 21)
    assert result == 42


def test_run_in_loader_thread_respects_configuration(monkeypatch):
    """Disabling background workers routes execution inline."""

    from visbrain import config

    cfg = config.get_config()
    previous = cfg.background_workers
    cfg.background_workers = False

    def fail():  # pragma: no cover - defensive
        raise AssertionError("Executor should not be invoked when disabled")

    monkeypatch.setattr(background_mod, "_get_executor", fail)
    try:
        future = run_in_loader_thread(lambda: "inline")
        assert future.result(timeout=1) == "inline"
    finally:
        cfg.background_workers = previous


def test_read_sleep_data_load_async():
    """Asynchronous construction of :class:`ReadSleepData` returns a future."""

    data = np.vstack(
        [np.linspace(0, 100, 200), np.linspace(50, 150, 200)]
    ).astype(np.float32)
    hypno = np.zeros(200, dtype=np.float32)
    future = ReadSleepData.load_async(
        data=data,
        channels=["C3", "C4"],
        sf=100.0,
        hypno=hypno,
        href=["art", "wake", "rem", "n1", "n2", "n3"],
        preload=True,
        use_mne=False,
        downsample=100.0,
        kwargs_mne={},
        annotations=None,
    )

    dataset = future.result(timeout=2)
    assert isinstance(dataset, ReadSleepData)
    assert dataset._data.shape == (2, 200)
    assert dataset._sf == pytest.approx(100.0)
