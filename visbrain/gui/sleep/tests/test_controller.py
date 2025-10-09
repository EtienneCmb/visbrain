"""Unit tests targeting the Sleep controller using synthetic fixtures."""

from __future__ import annotations

import datetime

import numpy as np

import pytest

try:  # pragma: no cover - optional Qt bindings
    from visbrain.qt import QtCore, QtWidgets
except ImportError:  # pragma: no cover - Qt not installed
    QtCore = QtWidgets = None

from visbrain.gui.sleep.model import SleepDataset
from visbrain.io.mneio import build_sleep_payload


pytestmark = [
    pytest.mark.skipif(QtWidgets is None, reason="Qt bindings are unavailable"),
]


def test_slider_signals_trigger_slots(sleep_controller, qtbot, monkeypatch):
    """Changing the slider emits the connected slot without manual calls."""

    called = []
    original = sleep_controller._fcn_slider_settings

    def tracker():
        called.append(True)
        return original()

    monkeypatch.setattr(sleep_controller, "_fcn_slider_settings", tracker)
    sleep_controller._SigSlStep.setValue(
        sleep_controller._SigSlStep.value() + 1
    )
    qtbot.waitUntil(lambda: called, timeout=1000)


def test_detection_workflow_and_persistence(sleep_controller, tmp_path):
    """Custom detections populate the table and can be saved/loaded."""

    def fake_detection(data, sf, time, hypno):
        return np.array([[10, 15], [20, 25]])

    sleep_controller.replace_detections("spindle", fake_detection)
    index = sleep_controller._ToolDetectType.findText("Spindles")
    sleep_controller._ToolDetectType.setCurrentIndex(index)
    sleep_controller._ToolDetectChan.setCurrentIndex(0)
    sleep_controller._ToolRdSelected.setChecked(True)
    sleep_controller._ToolDetectApply.click()
    assert sleep_controller._DetectLocations.rowCount() == 2

    file_all = tmp_path / "detections.npy"
    sleep_controller._save_all_detect(filename=str(file_all))
    assert file_all.exists()
    sleep_controller._load_detect_all(filename=str(file_all))

    sleep_controller._DetectLocations.selectRow(0)
    file_select = tmp_path / "selected_detect_Cz-Spindles.csv"
    sleep_controller._save_select_detect(filename=str(file_select))
    assert file_select.exists()
    sleep_controller._load_detect_select(filename=str(file_select))


def test_annotation_signals_update_table(sleep_controller, qtbot, monkeypatch):
    """Annotation buttons drive their slots via Qt signals."""

    called = []
    original = sleep_controller._fcn_annotate_add

    def tracker(*args, **kwargs):
        called.append(True)
        return original(*args, **kwargs)

    monkeypatch.setattr(sleep_controller, "_fcn_annotate_add", tracker)
    sleep_controller._AnnotateAdd.click()
    qtbot.waitUntil(lambda: called, timeout=1000)
    assert sleep_controller._AnnotateTable.rowCount() == 1

    sleep_controller._AnnotateRm.click()
    assert sleep_controller._AnnotateTable.rowCount() == 0


def test_save_and_load_helpers(sleep_controller, tmp_path):
    """Saving hypnograms and annotations works with synthetic data."""

    yes = QtWidgets.QMessageBox.Yes
    hyp_path = tmp_path / "hyp_data.txt"
    sleep_controller.saveHypData(filename=str(hyp_path), reply=yes)
    assert hyp_path.exists()

    anno_path = tmp_path / "annotations.csv"
    sleep_controller._save_annotation_table(filename=str(anno_path))
    assert anno_path.exists()

    numpy_annotations = np.array([5.0, 10.0, 15.0])
    sleep_controller._load_annotation_table(filename=numpy_annotations)
    assert sleep_controller._AnnotateTable.rowCount() == numpy_annotations.size


def test_async_loader_updates_model(sleep_controller, qtbot, synthetic_sleep_arrays):
    """Loading datasets in a worker thread hydrates the controller model."""

    data, hypno, channels, sf = synthetic_sleep_arrays
    scaled = data * 3.0

    timer_fired = []
    timer = QtCore.QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(lambda: timer_fired.append(True))
    timer.start(0)

    future = sleep_controller.load_dataset_async(
        data=scaled.copy(),
        channels=channels,
        sf=sf,
        hypno=hypno.copy(),
        href=["art", "wake", "rem", "n1", "n2", "n3"],
        preload=True,
        use_mne=False,
        downsample=sf,
        kwargs_mne={},
        annotations=None,
    )

    qtbot.waitUntil(lambda: timer_fired, timeout=1000)
    qtbot.waitUntil(future.done, timeout=3000)

    dataset = future.result(timeout=0.1)
    assert isinstance(dataset, SleepDataset)
    np.testing.assert_allclose(sleep_controller._model.data, scaled)
    assert sleep_controller._model.n_points == scaled.shape[1]


def test_async_loader_dialog_main_thread(
    sleep_controller, qtbot, synthetic_sleep_arrays, tmp_path, monkeypatch
):
    """File dialogs invoked from background loads run on the GUI thread."""

    data, hypno, channels, sf = synthetic_sleep_arrays
    dummy_path = tmp_path / "dummy.edf"
    dummy_path.write_bytes(b"")

    dialog_threads = []

    import visbrain.gui.threading as gui_threading

    invocations = []

    original_invoke = gui_threading.invoke_in_gui_thread

    def tracking_invoke(func, *args, **kwargs):
        invocations.append(func)
        return original_invoke(func, *args, **kwargs)

    monkeypatch.setattr(
        gui_threading,
        "invoke_in_gui_thread",
        tracking_invoke,
    )

    def fake_dialog(self, title, default, filters):
        dialog_threads.append(QtCore.QThread.currentThread())
        return str(dummy_path)

    monkeypatch.setattr("visbrain.io.read_sleep.dialog_load", fake_dialog)

    def fake_switch(file, ext, downsample, kwargs_mne=None):
        return build_sleep_payload(
            sf,
            sf,
            1,
            data.copy(),
            channels,
            data.shape[1],
            datetime.time(0, 0, 0),
            None,
            metadata={'source': str(dummy_path)},
        )

    monkeypatch.setattr("visbrain.io.read_sleep.sleep_switch", fake_switch)

    future = sleep_controller.load_dataset_async(
        data=None,
        channels=None,
        sf=sf,
        hypno=hypno.copy(),
        href=["art", "wake", "rem", "n1", "n2", "n3"],
        preload=True,
        use_mne=False,
        downsample=sf,
        kwargs_mne={},
    )

    qtbot.waitUntil(future.done, timeout=3000)
    future.result(timeout=0.1)

    assert dialog_threads, "dialog_load should be invoked"
    app = QtWidgets.QApplication.instance()
    assert app is not None
    assert all(thread is app.thread() for thread in dialog_threads)
    assert invocations, "invoke_in_gui_thread should wrap dialog calls"
