"""Unit tests targeting the Sleep controller using synthetic fixtures."""

from __future__ import annotations

import datetime
import time

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
    assert sleep_controller._model.file == str(dummy_path)


def test_async_loader_accepts_bids_directory(
    sleep_controller,
    synthetic_sleep_arrays,
    bids_sleep_directory,
    qtbot,
    monkeypatch,
):
    """BIDS recordings selected in dialogs hydrate the model correctly."""

    data, hypno, channels, sf = synthetic_sleep_arrays
    calls: dict[str, object] = {}

    class DummyDataset:
        def __init__(
            self,
            data_arg,
            channels_arg,
            sf_arg,
            hypno_arg,
            href_arg,
            preload,
            use_mne,
            downsample,
            kwargs_mne,
            annotations,
        ):
            base_data, base_hypno, base_channels, base_sf = synthetic_sleep_arrays
            calls["data"] = data_arg
            calls["kwargs_mne"] = dict(kwargs_mne)
            self.data = base_data.copy()
            self.hypno = base_hypno.copy()
            self.time = np.arange(base_data.shape[1], dtype=np.float32) / base_sf
            self.channels = list(channels_arg or base_channels)
            self.href = list(href_arg or ["art", "wake", "rem", "n1", "n2", "n3"])
            self.hconv = {idx: idx for idx, _ in enumerate(self.href)}
            self.sf = float(sf_arg or base_sf)
            self.sfori = float(sf_arg or base_sf)
            self.dsf = int(downsample or base_sf)
            self.n_points = self.data.shape[1]
            self.file = str(data_arg) if isinstance(data_arg, str) else None
            self.annotations = (
                np.array(annotations)
                if annotations is not None
                else np.empty((0, 1))
            )

    monkeypatch.setattr("visbrain.gui.sleep.controller.SleepDataset", DummyDataset)

    future = sleep_controller.load_dataset_async(
        data=str(bids_sleep_directory.recording),
        channels=channels,
        sf=sf,
        hypno=hypno.copy(),
        href=list(sleep_controller._model.href),
        preload=True,
        use_mne=True,
        downsample=sf,
        kwargs_mne={"bids_root": str(bids_sleep_directory.root)},
        annotations=None,
    )

    qtbot.waitUntil(future.done, timeout=3000)
    future.result(timeout=0.1)

    assert calls["data"] == str(bids_sleep_directory.recording)
    assert calls["kwargs_mne"]["bids_root"] == str(bids_sleep_directory.root)
    assert sleep_controller._model.file == str(bids_sleep_directory.recording)


def test_async_loader_error_logging(
    sleep_controller, qtbot, caplog, monkeypatch
):
    """Failures raised in worker threads surface through controller logs."""

    class ExplodingDataset:
        def __init__(*args, **kwargs):  # noqa: D401 - stub signature
            raise RuntimeError("loader boom")

    monkeypatch.setattr("visbrain.gui.sleep.controller.SleepDataset", ExplodingDataset)
    caplog.set_level("ERROR", logger="visbrain")

    future = sleep_controller.load_dataset_async(
        data=np.zeros((2, 10), dtype=np.float32),
        channels=["C1", "C2"],
        sf=100.0,
        hypno=np.zeros(10, dtype=np.float32),
        href=["art", "wake"],
        preload=True,
        use_mne=False,
        downsample=100.0,
        kwargs_mne={},
        annotations=None,
    )

    with pytest.raises(RuntimeError):
        future.result(timeout=1.0)

    qtbot.waitUntil(
        lambda: any(
            "Asynchronous sleep load failed" in record.message
            for record in caplog.records
        ),
        timeout=1000,
    )
    assert sleep_controller._model.file is None


@pytest.mark.performance
def test_async_loader_threading_benchmark(
    sleep_controller, synthetic_sleep_arrays, monkeypatch
):
    """Threaded loads should return control faster than inline execution."""

    from visbrain.io import background

    data, hypno, channels, sf = synthetic_sleep_arrays

    class SlowSleepDataset(SleepDataset):
        def __init__(self, *args, **kwargs):
            time.sleep(0.05)
            super().__init__(*args, **kwargs)

    monkeypatch.setattr("visbrain.gui.sleep.controller.SleepDataset", SlowSleepDataset)

    background.shutdown_loader_threads(wait=True)
    monkeypatch.setenv("VISBRAIN_BACKGROUND_WORKERS", "0")
    start_inline = time.perf_counter()
    future_inline = sleep_controller.load_dataset_async(
        data=data.copy(),
        channels=list(channels),
        sf=sf,
        hypno=hypno.copy(),
        href=list(sleep_controller._model.href),
        preload=True,
        use_mne=False,
        downsample=sf,
        kwargs_mne={},
        annotations=None,
    )
    inline_elapsed = time.perf_counter() - start_inline
    future_inline.result(timeout=5.0)

    monkeypatch.setenv("VISBRAIN_BACKGROUND_WORKERS", "1")
    background.shutdown_loader_threads(wait=True)
    start_threaded = time.perf_counter()
    future_threaded = sleep_controller.load_dataset_async(
        data=data.copy(),
        channels=list(channels),
        sf=sf,
        hypno=hypno.copy(),
        href=list(sleep_controller._model.href),
        preload=True,
        use_mne=False,
        downsample=sf,
        kwargs_mne={},
        annotations=None,
    )
    threaded_elapsed = time.perf_counter() - start_threaded
    future_threaded.result(timeout=5.0)

    print(f"inline_call={inline_elapsed:.4f}s threaded_call={threaded_elapsed:.4f}s")
    assert threaded_elapsed < inline_elapsed * 0.5
