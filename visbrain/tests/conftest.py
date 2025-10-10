"""Shared fixtures available across Visbrain test suites."""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import numpy as np
import pytest


class BidsDataset(NamedTuple):
    """Paths composing a synthetic BIDS directory used in tests."""

    root: Path
    recording: Path


@pytest.fixture
def isolated_cache_dir(monkeypatch, tmp_path_factory) -> Path:
    """Point the cache manager at a temporary directory during tests."""

    root = tmp_path_factory.mktemp("visbrain-cache")
    monkeypatch.setenv("VISBRAIN_DATA_DIR", str(root))
    from visbrain.io.path import cache_manager

    cache_manager.cleanup_all()
    cache_manager.cleanup_all(category="data")
    yield root
    cache_manager.cleanup_all()
    cache_manager.cleanup_all(category="data")


@pytest.fixture
def bids_sleep_directory(tmp_path_factory) -> BidsDataset:
    """Create a minimal BIDS-like hierarchy with placeholder recordings."""

    root = tmp_path_factory.mktemp("bids-sleep")
    eeg_dir = root / "sub-01" / "ses-test" / "eeg"
    eeg_dir.mkdir(parents=True)
    recording = eeg_dir / "sub-01_ses-test_task-rest_run-1_eeg.edf"
    recording.write_bytes(b"EDF")
    (eeg_dir / "sub-01_ses-test_task-rest_run-1_eeg.json").write_text("{}")
    (eeg_dir / "participants.tsv").write_text("participant_id\nsub-01\n")
    return BidsDataset(root=root, recording=recording)


@pytest.fixture(scope="session")
def synthetic_sleep_arrays() -> tuple[np.ndarray, np.ndarray, list[str], float]:
    """Return deterministic arrays used across multiple tests."""

    rng = np.random.default_rng(1337)
    data = rng.standard_normal((2, 400)).astype(np.float32)
    hypno = np.zeros(400, dtype=np.float32)
    hypno[50:100] = 1
    hypno[200:260] = 4
    channels = ["Cz", "Pz"]
    sf = 100.0
    return data, hypno, channels, sf


__all__ = [
    "BidsDataset",
    "bids_sleep_directory",
    "isolated_cache_dir",
    "synthetic_sleep_arrays",
]
