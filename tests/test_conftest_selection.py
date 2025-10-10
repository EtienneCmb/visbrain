"""Regression tests for :mod:`conftest` selection helpers."""
from __future__ import annotations

from pathlib import Path

import pytest

import conftest as visbrain_conftest


def test_pytest_ignore_collect_skips_installed_gui_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Installed ``visbrain`` GUI paths should be ignored when GUI tests are off."""

    fake_site_packages = tmp_path / "site-packages"
    package_root = fake_site_packages / "visbrain"
    package_root.mkdir(parents=True)

    fake_test = package_root / "gui" / "tests" / "test_dummy.py"
    fake_test.parent.mkdir(parents=True)
    fake_test.touch()

    monkeypatch.setattr(
        visbrain_conftest,
        "_GUI_MARKER_PATHS",
        visbrain_conftest._build_gui_marker_paths(
            (package_root, visbrain_conftest._REPO_PACKAGE_ROOT)
        ),
    )
    monkeypatch.setattr(visbrain_conftest, "_RUNNING_GUI_TESTS", False)

    assert visbrain_conftest.pytest_ignore_collect(fake_test, config=None)
