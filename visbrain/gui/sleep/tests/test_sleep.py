"""Integration tests for the Sleep façade using headless fixtures."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

# SleepDataset can be imported without a GUI stack but the controller/view
# require a functioning Qt binding.  Import lazily so the module still loads
# when Qt is missing and the tests can be skipped gracefully.
try:  # pragma: no cover - optional Qt bindings
    from visbrain.gui.sleep.controller import SleepController
    from visbrain.gui.sleep.model import SleepDataset
    from visbrain.gui.sleep.view import SleepView
except Exception:  # pragma: no cover - Qt not installed
    SleepController = SleepDataset = SleepView = None

try:  # pragma: no cover - optional Qt bindings
    from visbrain.qt import QtWidgets
except ImportError:  # pragma: no cover - Qt not installed
    QtWidgets = None


pytestmark = [
    pytest.mark.skipif(
        QtWidgets is None or SleepController is None,
        reason="Qt bindings are unavailable",
    ),
]


def test_facade_components(sleep_facade):
    """The façade wires the model, view and controller together."""

    assert isinstance(sleep_facade.model, SleepDataset)
    assert isinstance(sleep_facade.view, SleepView)
    assert isinstance(sleep_facade.controller, SleepController)
    assert sleep_facade.model is sleep_facade.controller._model
    assert sleep_facade.view is sleep_facade.controller._view


def test_visual_scenegraph(sleep_facade):
    """Channel visuals attach to the channel canvas scene."""

    node = sleep_facade._chan.node[0]
    canvas = sleep_facade._chanCanvas[0]
    assert node.parent is canvas.wc.scene
    assert sleep_facade._chan.mesh[0].parent is node


def test_detection_flow_through_facade(sleep_facade, tmp_path):
    """Custom detections propagate through the full GUI stack."""

    def fake_detection(data, sf, time, hypno):
        return np.array([[5, 10], [15, 20]])

    sleep_facade.replace_detections("spindle", fake_detection)
    combo_index = sleep_facade._ToolDetectType.findText("Spindles")
    sleep_facade._ToolDetectType.setCurrentIndex(combo_index)
    sleep_facade._ToolDetectChan.setCurrentIndex(0)
    sleep_facade._ToolDetectApply.click()
    assert sleep_facade._DetectLocations.rowCount() == 2

    file_all = tmp_path / "facade_detections.npy"
    sleep_facade._save_all_detect(filename=str(file_all))
    assert file_all.exists()
    sleep_facade._load_detect_all(filename=str(file_all))


def test_annotation_roundtrip(sleep_facade):
    """Annotation helpers work without entering the Qt event loop."""

    sleep_facade._AnnotateAdd.click()
    sleep_facade._AnnotateTable.item(0, 2).setText("Fixture annotation")
    assert sleep_facade._AnnotateTable.rowCount() == 1

    sleep_facade._AnnotateRm.click()
    assert sleep_facade._AnnotateTable.rowCount() == 0


def test_facade_save_helpers(sleep_facade, tmp_path):
    """Saving through the façade reuses controller helpers headlessly."""

    hyp_path = tmp_path / "hyp_data.txt"
    sleep_facade.saveHypData(
        filename=str(hyp_path), reply=QtWidgets.QMessageBox.Yes
    )
    assert hyp_path.exists()

    anno_path = tmp_path / "annotations.csv"
    sleep_facade._save_annotation_table(filename=str(anno_path))
    assert anno_path.exists()

    numpy_annotations = np.array([2.0, 4.0, 6.0])
    sleep_facade._load_annotation_table(filename=numpy_annotations)
    assert sleep_facade._AnnotateTable.rowCount() == numpy_annotations.size


def test_sleep_cache_session_reuse(sleep_facade):
    """Tmp sessions are stable within a run and cleaned on demand."""

    first_session = sleep_facade._path_to_tmp_folder()
    second_session = sleep_facade._path_to_tmp_folder()
    assert first_session == second_session
    assert Path(first_session).exists()

    sleep_facade._clean_tmp_folder()
    assert not Path(first_session).exists()

    third_session = sleep_facade._path_to_tmp_folder()
    assert third_session != first_session
