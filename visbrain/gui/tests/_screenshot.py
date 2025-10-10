"""Utilities for deterministic GUI screenshot regression tests."""
from __future__ import annotations

import contextlib
import os
import random
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, ContextManager, Iterator

import imageio.v3 as iio
import numpy as np
from PIL import Image

from visbrain.config import get_config, qt_app, vispy_app
from visbrain.qt import QtCore, QtGui, QtWidgets

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_OPENGL", "software")
os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
os.environ.setdefault("VISPY_APP_BACKEND", "pyside6")
os.environ.setdefault("VISPY_USE_APP", "pyside6")
os.environ.setdefault("MPLBACKEND", "Agg")

BASELINE_DIR = Path(__file__).with_name("baseline")
UPDATE_BASELINES = bool(os.environ.get("VISBRAIN_UPDATE_SCREENSHOTS"))


@dataclass(frozen=True)
class GuiSpec:
    """Description of a GUI module used for screenshot regression tests."""

    name: str
    factory: Callable[[], ContextManager[Any] | Any]
    widget_getter: Callable[[Any], QtWidgets.QWidget] = field(
        default=lambda instance: instance
    )
    size: tuple[int, int] = (1280, 720)
    tolerance: int = 0
    subprocess_capture: Callable[[], np.ndarray] | None = None

    @property
    def baseline_path(self) -> Path:
        return BASELINE_DIR / f"{self.name}.png"


def _reset_random_seeds() -> None:
    random.seed(0)
    np.random.seed(0)


def _prepare_qt_attributes() -> None:
    """Configure Qt attributes before any QApplication is created."""

    try:
        QtWidgets.QApplication.setAttribute(
            QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling, False
        )
    except AttributeError:  # pragma: no cover - older Qt bindings
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, False)
    try:
        QtWidgets.QApplication.setAttribute(
            QtCore.Qt.ApplicationAttribute.AA_Use96Dpi, True
        )
    except AttributeError:  # pragma: no cover - older Qt bindings
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_Use96Dpi, True)
    try:
        QtWidgets.QApplication.setAttribute(
            QtCore.Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True
        )
    except AttributeError:  # pragma: no cover - older Qt bindings
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts, True)
    try:
        QtWidgets.QApplication.setAttribute(
            QtCore.Qt.ApplicationAttribute.AA_UseSoftwareOpenGL, True
        )
    except AttributeError:  # pragma: no cover - older Qt bindings
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseSoftwareOpenGL, True)


def _ensure_runtime_configuration() -> None:
    cfg = get_config()
    cfg.show_gui = False
    cfg.vispy_backend = "pyside6"
    try:
        import vispy

        vispy.use(gl="egl")
    except Exception:
        pass


def _drain_events(app: QtWidgets.QApplication, *, cycles: int = 40) -> None:
    for _ in range(cycles):
        app.processEvents(QtCore.QEventLoop.AllEvents, 20)


def _close_if_possible(obj: Any) -> None:
    close = getattr(obj, "close", None)
    if callable(close):
        close()

    cleanup = getattr(obj, "cleanup", None)
    if callable(cleanup):
        cleanup()


def _enter_value(stack: contextlib.ExitStack, value: Any) -> Any:
    if isinstance(value, contextlib.AbstractContextManager):
        return stack.enter_context(value)
    if hasattr(value, "__enter__") and hasattr(value, "__exit__"):
        return stack.enter_context(value)  # type: ignore[arg-type]
    stack.callback(_close_if_possible, value)
    return value


def _grab_widget(widget: QtWidgets.QWidget) -> np.ndarray:
    pixmap = widget.grab()
    image = pixmap.toImage().convertToFormat(QtGui.QImage.Format_RGBA8888)
    width = image.width()
    height = image.height()
    ptr = image.constBits()
    if hasattr(ptr, "setsize"):
        ptr.setsize(image.byteCount())
        buffer = bytes(ptr)
    else:
        buffer = ptr.tobytes()
    array = np.frombuffer(buffer, dtype=np.uint8)
    return array.reshape((height, width, 4))


def capture_screenshot(
    factory: Callable[[], ContextManager[Any] | Any],
    *,
    widget_getter: Callable[[Any], QtWidgets.QWidget] | None = None,
    size: tuple[int, int] = (1280, 720),
    use_vispy: bool = True,
) -> np.ndarray:
    """Launch a GUI module and return a screenshot as an ``ndarray``."""

    _reset_random_seeds()
    _prepare_qt_attributes()
    _ensure_runtime_configuration()
    widget_getter = widget_getter or (lambda instance: instance)

    with contextlib.ExitStack() as stack:
        app = stack.enter_context(qt_app(force=True, reset=True))
        if use_vispy:
            stack.enter_context(vispy_app(force=True, reset=True))
        if app is None:
            raise RuntimeError("Qt application could not be created")
        instance = _enter_value(stack, factory())
        widget = widget_getter(instance)
        if widget is None:
            raise RuntimeError("Widget getter returned None")
        widget.resize(*size)
        widget.show()
        widget.raise_()
        _drain_events(app)
        screenshot = _grab_widget(widget)
        _drain_events(app, cycles=5)
    return screenshot


def render_spec(spec: GuiSpec) -> np.ndarray:
    if spec.subprocess_capture is not None:
        return spec.subprocess_capture()
    return capture_screenshot(
        spec.factory,
        widget_getter=spec.widget_getter,
        size=spec.size,
    )


def save_png(path: Path, data: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.fromarray(data)
    image.save(path, format="PNG")


def load_png(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.array(image)


def max_pixel_delta(reference: np.ndarray, candidate: np.ndarray) -> int:
    if reference.shape != candidate.shape:
        raise AssertionError(
            f"Screenshot shape mismatch: {reference.shape} != {candidate.shape}"
        )
    delta = np.abs(reference.astype(np.int16) - candidate.astype(np.int16))
    return int(delta.max(initial=0))


def _capture_brain_subprocess() -> np.ndarray:
    import tempfile
    import textwrap

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        output = tmp_path / "brain_capture.png"

        from string import Template

        script_template = Template(
            """
            import os
            import sys
            import tempfile
            from pathlib import Path

            import numpy as np

            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
            os.environ.setdefault("QT_OPENGL", "software")
            os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
            os.environ.setdefault("VISPY_APP_BACKEND", "pyside6")
            os.environ.setdefault("VISPY_USE_APP", "pyside6")
            os.environ.setdefault("MPLBACKEND", "Agg")

            from visbrain.config import get_config, qt_app, vispy_app
            from visbrain.gui.brain import Brain
            from visbrain.objects import BrainObj, CrossSecObj, RoiObj, VolumeObj
            from visbrain.objects.visbrain_obj import VisbrainObject
            from visbrain.qt import QtCore

            cfg = get_config()
            cfg.show_gui = False
            cfg.vispy_backend = "pyside6"

            vertices = np.array(
                [
                    (-20.0, -20.0, -20.0),
                    (20.0, -20.0, -20.0),
                    (-20.0, 20.0, -20.0),
                    (-20.0, -20.0, 20.0),
                    (20.0, 20.0, 20.0),
                ],
                dtype=np.float32,
            )
            faces = np.array(
                [
                    (0, 1, 2),
                    (0, 1, 3),
                    (0, 2, 3),
                    (1, 2, 4),
                    (1, 3, 4),
                    (2, 3, 4),
                ],
                dtype=np.int32,
            )

            brain_obj = BrainObj(
                "screenshot_brain",
                vertices=vertices,
                faces=faces,
                translucent=False,
                verbose="error",
            )

            volume = np.zeros((4, 4, 4), dtype=np.float32)
            hdr = np.eye(4, dtype=np.float32)
            roi_labels = np.array(["Region"], dtype=object)
            roi_index = np.array([0], dtype=np.int32)

            with tempfile.TemporaryDirectory() as data_tmp:
                data_root = Path(data_tmp)
                volume_path = data_root / "screenshot_volume.npz"
                roi_path = data_root / "screenshot_roi.npz"
                cross_path = data_root / "screenshot_cross.npz"
                np.savez(
                    volume_path,
                    vol=volume,
                    hdr=hdr,
                    labels=np.empty((0,), dtype=np.int32),
                    index=np.empty((0,), dtype=np.int32),
                )
                np.savez(
                    roi_path,
                    vol=volume.astype(np.int16),
                    hdr=hdr,
                    labels=roi_labels,
                    index=roi_index,
                )
                np.savez(
                    cross_path,
                    vol=volume,
                    hdr=hdr,
                    labels=np.empty((0,), dtype=np.int32),
                    index=np.empty((0,), dtype=np.int32),
                )

                mapping = {
                    "screenshot_volume.npz": str(volume_path),
                    "screenshot_roi.npz": str(roi_path),
                    "screenshot_cross.npz": str(cross_path),
                }

                original_get_file = VisbrainObject._df_get_file
                original_get_downloaded = VisbrainObject._df_get_downloaded

                def _patched_get_file(self, file, download=True):
                    if file in mapping:
                        return mapping[file]
                    return original_get_file(self, file, download)

                def _patched_get_downloaded(self, **kwargs):
                    downloaded = list(original_get_downloaded(self, **kwargs))
                    for key in mapping:
                        if key not in downloaded:
                            downloaded.append(key)
                    return downloaded

                setattr(VisbrainObject, "_df_get_file", _patched_get_file)
                setattr(VisbrainObject, "_df_get_downloaded", _patched_get_downloaded)
                try:
                    volume_obj = VolumeObj(
                        "screenshot_volume",
                        preload=True,
                        verbose="error",
                    )
                    roi_obj = RoiObj(
                        "screenshot_roi",
                        preload=True,
                        verbose="error",
                    )
                    cross_sec_obj = CrossSecObj(
                        "screenshot_cross", preload=True, verbose="error"
                    )

                    with qt_app(force=True, reset=True) as app, vispy_app(
                        force=True, reset=True
                    ):
                        gui = Brain(
                            brain_obj=brain_obj,
                            vol_obj=volume_obj,
                            roi_obj=roi_obj,
                            cross_sec_obj=cross_sec_obj,
                            bgcolor="black",
                            verbose="error",
                        )
                        gui.resize(1280, 720)
                        gui.show()
                        gui.raise_()
                        for _ in range(80):
                            app.processEvents(QtCore.QEventLoop.AllEvents, 50)
                        pixmap = gui.grab()
                        pixmap.save(str(Path("$OUTPUT")))
                        gui.close()
                finally:
                    setattr(VisbrainObject, "_df_get_file", original_get_file)
                    setattr(
                        VisbrainObject,
                        "_df_get_downloaded",
                        original_get_downloaded,
                    )

            os._exit(0)
            """
        )

        env = os.environ.copy()
        script = textwrap.dedent(script_template.substitute(OUTPUT=str(output)))
        subprocess.run([sys.executable, "-c", script], check=True, env=env)
        return iio.imread(output)


@contextlib.contextmanager
def _signal_factory() -> Iterator[Any]:
    from visbrain.gui.signal import Signal
    from visbrain.qt import QtGui, QtWidgets

    time = np.linspace(0.0, 2.0, 400, dtype=np.float32)
    wave = np.sin(2 * np.pi * 5 * time)
    envelope = np.cos(2 * np.pi * 1 * time)
    data = np.vstack([wave, envelope])

    if not hasattr(QtWidgets, "QAction"):
        QtWidgets.QAction = QtGui.QAction  # type: ignore[attr-defined]

    gui = Signal(data=data, sf=200.0, verbose="error")
    try:
        yield gui
    finally:
        gui.close()


@contextlib.contextmanager
def _sleep_factory() -> Iterator[Any]:
    from visbrain.gui.sleep import Sleep
    from visbrain.qt import QtWidgets
    from visbrain.qt import QtGui

    time = np.linspace(0.0, 60.0, 600, dtype=np.float32)
    channel_a = np.sin(2 * np.pi * 1.5 * time)
    channel_b = np.cos(2 * np.pi * 0.75 * time)
    data = np.vstack([channel_a, channel_b])
    hypno = np.tile([0, 1, 2, 3, 2, 1], 100)[: data.shape[1]]

    original_set_column = QtWidgets.QGridLayout.setColumnStretch

    def _patched_set_column(layout, column, stretch=None):
        if stretch is None and isinstance(column, str):
            parts = [part.strip() for part in column.split(',') if part.strip()]
            for idx, value in enumerate(parts):
                try:
                    original_set_column(layout, idx, int(value))
                except (TypeError, ValueError):
                    continue
            return None
        return original_set_column(layout, column, stretch)

    QtWidgets.QGridLayout.setColumnStretch = _patched_set_column  # type: ignore[assignment]

    original_shortcut = QtGui.QShortcut

    class _Signal:
        def connect(self, *_args, **_kwargs) -> None:  # pragma: no cover - GUI stub
            return None

    class _NoOpShortcut:
        def __init__(self, *args, **kwargs) -> None:  # pragma: no cover - GUI stub
            self._enabled = True
            self.activated = _Signal()

        def setEnabled(self, value: bool) -> None:  # pragma: no cover - GUI stub
            self._enabled = bool(value)

        def setContext(self, *_args, **_kwargs) -> None:  # pragma: no cover - GUI stub
            return None

    QtGui.QShortcut = _NoOpShortcut  # type: ignore[assignment]

    gui = Sleep(data=data, hypno=hypno, sf=10.0, downsample=2.0, verbose="error")
    try:
        yield gui
    finally:
        QtWidgets.QGridLayout.setColumnStretch = original_set_column  # type: ignore[assignment]
        QtGui.QShortcut = original_shortcut  # type: ignore[assignment]
        gui.close()


def _capture_signal_subprocess() -> np.ndarray:
    import tempfile
    import textwrap

    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "signal_capture.png"
        from string import Template

        script_template = Template(
            """
            import os
            import numpy as np
            from pathlib import Path

            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
            os.environ.setdefault("QT_OPENGL", "software")
            os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
            os.environ.setdefault("VISPY_APP_BACKEND", "pyside6")
            os.environ.setdefault("VISPY_USE_APP", "pyside6")
            os.environ.setdefault("MPLBACKEND", "Agg")

            from visbrain.config import get_config, qt_app, vispy_app
            from visbrain.gui.signal import Signal
            from visbrain.qt import QtCore, QtGui, QtWidgets
            from visbrain.gui.tests import _screenshot as utils

            utils._reset_random_seeds()
            utils._prepare_qt_attributes()

            cfg = get_config()
            cfg.show_gui = False
            cfg.vispy_backend = "pyside6"

            time = np.linspace(0.0, 2.0, 400, dtype=np.float32)
            wave = np.sin(2 * np.pi * 5 * time)
            envelope = np.cos(2 * np.pi * 1 * time)
            data = np.vstack([wave, envelope])

            if not hasattr(QtWidgets, "QAction"):
                setattr(QtWidgets, "QAction", QtGui.QAction)

            with qt_app(force=True, reset=True) as app, vispy_app(
                force=True,
                reset=True,
            ):
                gui = Signal(data=data, sf=200.0, verbose="error")
                gui.resize(1280, 720)
                gui.show()
                gui.raise_()
                for _ in range(80):
                    app.processEvents(QtCore.QEventLoop.AllEvents, 50)
                pixmap = gui.grab()
                pixmap.save(str(Path("$OUTPUT")))
                gui.close()

            os._exit(0)
            """
        )

        env = os.environ.copy()
        script = textwrap.dedent(script_template.substitute(OUTPUT=str(output)))
        subprocess.run([sys.executable, "-c", script], check=True, env=env)
        return iio.imread(output)


def _capture_sleep_subprocess() -> np.ndarray:
    import tempfile
    import textwrap

    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "sleep_capture.png"
        from string import Template

        script_template = Template(
            """
            import os
            import numpy as np
            from pathlib import Path

            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
            os.environ.setdefault("QT_OPENGL", "software")
            os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
            os.environ.setdefault("VISPY_APP_BACKEND", "pyside6")
            os.environ.setdefault("VISPY_USE_APP", "pyside6")
            os.environ.setdefault("MPLBACKEND", "Agg")

            from visbrain.config import get_config, qt_app, vispy_app
            from visbrain.gui.sleep import Sleep
            from visbrain.qt import QtCore, QtWidgets, QtGui
            from visbrain.gui.tests import _screenshot as utils

            utils._reset_random_seeds()
            utils._prepare_qt_attributes()

            cfg = get_config()
            cfg.show_gui = False
            cfg.vispy_backend = "pyside6"

            time = np.linspace(0.0, 60.0, 600, dtype=np.float32)
            channel_a = np.sin(2 * np.pi * 1.5 * time)
            channel_b = np.cos(2 * np.pi * 0.75 * time)
            data = np.vstack([channel_a, channel_b])
            hypno = np.tile([0, 1, 2, 3, 2, 1], 100)[: data.shape[1]]

            original_set_column = QtWidgets.QGridLayout.setColumnStretch

            def _patched_set_column(layout, column, stretch=None):
                if stretch is None and isinstance(column, str):
                    parts = [part.strip() for part in column.split(',') if part.strip()]
                    for idx, value in enumerate(parts):
                        try:
                            original_set_column(layout, idx, int(value))
                        except (TypeError, ValueError):
                            continue
                    return None
                return original_set_column(layout, column, stretch)

            setattr(QtWidgets.QGridLayout, "setColumnStretch", _patched_set_column)

            original_shortcut = QtGui.QShortcut

            class _Signal:
                def connect(self, *args, **kwargs):
                    return None

            class _NoOpShortcut:
                def __init__(self, *args, **kwargs):
                    self._enabled = True
                    self.activated = _Signal()

                def setEnabled(self, value):
                    self._enabled = bool(value)

                def setContext(self, *args, **kwargs):
                    return None

            QtGui.QShortcut = _NoOpShortcut

            try:
                with qt_app(force=True, reset=True) as app, vispy_app(
                    force=True,
                    reset=True,
                ):
                    gui = Sleep(
                        data=data,
                        hypno=hypno,
                        sf=10.0,
                        downsample=2.0,
                        verbose="error",
                    )
                    widget = gui.q_widget
                    widget.resize(1280, 720)
                    widget.show()
                    widget.raise_()
                    for _ in range(80):
                        app.processEvents(QtCore.QEventLoop.AllEvents, 50)
                    pixmap = widget.grab()
                    pixmap.save(str(Path("$OUTPUT")))
                    gui.close()
            finally:
                setattr(QtWidgets.QGridLayout, "setColumnStretch", original_set_column)
                QtGui.QShortcut = original_shortcut

            os._exit(0)
            """
        )

        env = os.environ.copy()
        script = textwrap.dedent(script_template.substitute(OUTPUT=str(output)))
        subprocess.run([sys.executable, "-c", script], check=True, env=env)
        return iio.imread(output)


def _capture_figure_subprocess() -> np.ndarray:
    import tempfile
    import textwrap

    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "figure_capture.png"
        from string import Template

        script_template = Template(
            """
            import os
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
            os.environ['QT_OPENGL'] = 'software'
            os.environ['PYOPENGL_PLATFORM'] = 'egl'
            os.environ['VISPY_APP_BACKEND'] = 'pyside6'
            os.environ['VISPY_USE_APP'] = 'pyside6'
            os.environ['MPLBACKEND'] = 'Agg'
            import matplotlib
            matplotlib.use('Agg', force=True)
            import numpy as np
            import imageio.v3 as iio
            import tempfile
            from pathlib import Path
            from visbrain.config import get_config, qt_app
            from visbrain.qt import QtCore
            from visbrain.gui.figure.figure import FigureGUI

            cfg = get_config()
            cfg.show_gui = False

            with qt_app(force=True, reset=True) as app:
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmp = Path(tmpdir)
                    base = np.linspace(0, 255, 96, dtype=np.uint8)
                    base = np.tile(base, (96, 1))
                    files = []
                    for idx in range(3):
                        panel = np.dstack([
                            np.roll(base, idx * 5, axis=0),
                            np.roll(base, idx * 7, axis=1),
                            np.full_like(base, 90 + idx * 40),
                        ])
                        path = tmp / ('panel_%d.png' % idx)
                        iio.imwrite(path, panel, extension='.png')
                        files.append(path)
                    gui = FigureGUI(files=[str(path) for path in files])
                    gui._window.resize(900, 620)
                    gui._window.show()
                    for _ in range(10):
                        app.processEvents(QtCore.QEventLoop.AllEvents, 50)
                    pixmap = gui._window.grab()
                    pixmap.save(str(Path("$OUTPUT")))
                    gui.close()
            """
        )
        env = os.environ.copy()
        script = textwrap.dedent(script_template.substitute(OUTPUT=str(output)))
        subprocess.run([sys.executable, "-c", script], check=True, env=env)
        return iio.imread(output)


@contextlib.contextmanager
def _figure_factory() -> Iterator[Any]:
    import tempfile

    import matplotlib

    matplotlib.use("Agg", force=True)
    from visbrain.gui.figure.figure import FigureGUI

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        gradients: list[Path] = []
        base = np.linspace(0, 255, 128, dtype=np.uint8)
        base = np.tile(base, (128, 1))
        for idx in range(3):
            panel = np.dstack(
                [
                    np.roll(base, shift=idx * 8, axis=0),
                    np.roll(base, shift=idx * 12, axis=1),
                    np.full_like(base, 80 + idx * 40),
                ]
            )
            path = tmp_path / f"panel_{idx}.png"
            iio.imwrite(path, panel, extension=".png")
            gradients.append(path)
        gui = FigureGUI(files=[str(path) for path in gradients])
        try:
            yield gui
        finally:
            gui.close()


@contextlib.contextmanager
def _brain_visual_canvas() -> Iterator[QtWidgets.QWidget]:
    """Return a VisbrainCanvas hosting a minimal BrainVisual."""

    from visbrain.objects.scene_obj import VisbrainCanvas
    from visbrain.visuals.brain_visual import BrainMesh
    from vispy.scene.cameras import TurntableCamera

    vertices = np.array(
        [
            (-0.6, -0.6, -0.4),
            (0.6, -0.6, -0.4),
            (-0.6, 0.6, -0.4),
            (-0.4, -0.4, 0.6),
            (0.4, 0.4, 0.6),
        ],
        dtype=np.float32,
    )
    faces = np.array(
        [
            (0, 1, 2),
            (0, 1, 3),
            (0, 2, 3),
            (1, 2, 4),
            (1, 3, 4),
            (2, 3, 4),
        ],
        dtype=np.uint32,
    )
    base_normal = np.array([[0.0, 0.0, 1.0]], dtype=np.float32)
    normals = np.tile(base_normal, (vertices.shape[0], 1))

    camera = TurntableCamera(
        fov=40.0,
        elevation=25.0,
        azimuth=45.0,
        distance=2.5,
        center=(0.0, 0.0, 0.0),
    )
    canvas = VisbrainCanvas(axis=False, bgcolor="white", camera=camera, show=False)
    BrainMesh(vertices=vertices, faces=faces, normals=normals, parent=canvas.wc.scene)

    widget = canvas.canvas.native
    try:
        yield widget
    finally:
        canvas.canvas.close()


SCREENSHOT_SPECS: tuple[GuiSpec, ...] = (
    GuiSpec(
        "brain",
        factory=lambda: contextlib.nullcontext(None),
        subprocess_capture=_capture_brain_subprocess,
    ),
    GuiSpec(
        "signal",
        factory=_signal_factory,
        subprocess_capture=_capture_signal_subprocess,
    ),
    GuiSpec(
        "sleep",
        factory=_sleep_factory,
        widget_getter=lambda gui: gui.q_widget,
        subprocess_capture=_capture_sleep_subprocess,
    ),
    GuiSpec(
        "brain-visual-canvas",
        factory=_brain_visual_canvas,
        size=(720, 480),
        tolerance=1,
    ),
    GuiSpec(
        "figure",
        factory=_figure_factory,
        widget_getter=lambda gui: gui._window,
        size=(1000, 700),
        tolerance=1,
        subprocess_capture=_capture_figure_subprocess,
    ),
)
__all__ = [
    "BASELINE_DIR",
    "GuiSpec",
    "SCREENSHOT_SPECS",
    "UPDATE_BASELINES",
    "capture_screenshot",
    "load_png",
    "max_pixel_delta",
    "render_spec",
    "save_png",
]

