"""Top-level Sleep façade assembling model, view and controller."""

from __future__ import annotations

from typing import Optional

from visbrain._pyqt_module import _PyQtModule
from visbrain.config import PROFILER, ensure_qt_app, get_config
from visbrain.gui._accessibility import install_action_shortcuts
from visbrain.qt import QtCore, QtWidgets

from .controller import SleepController
from .model import SleepDataset
from .view import SleepView


class Sleep(_PyQtModule):
    """Visualize and edit sleep data using a model/view/controller split."""

    def __init__(
        self,
        data=None,
        hypno=None,
        config_file=None,
        annotations=None,
        channels=None,
        sf=None,
        downsample=100.0,
        axis=True,
        href=None,
        preload=True,
        use_mne=False,
        kwargs_mne=None,
        *,
        verbose=None,
        model: Optional[SleepDataset] = None,
        view: Optional[SleepView] = None,
        controller: Optional[SleepController] = None,
    ) -> None:
        if href is None:
            href = ['art', 'wake', 'rem', 'n1', 'n2', 'n3']
        if kwargs_mne is None:
            kwargs_mne = {}

        super().__init__(verbose=verbose, icon='sleep_icon.svg')
        ensure_qt_app(force=True)
        self._visuals_timer_scheduled = False
        self._visual_retry_count = 0
        self._view_ready_filter = None
        cfg = get_config()

        PROFILER("Import file", as_type='title')
        if model is None:
            model = SleepDataset(
                data,
                channels,
                sf,
                hypno,
                href,
                preload,
                use_mne,
                downsample,
                kwargs_mne,
                annotations,
            )
        elif not isinstance(model, SleepDataset):
            raise TypeError("model must be an instance of SleepDataset")

        self._model = model

        if view is not None and not isinstance(view, SleepView):
            raise TypeError("view must be an instance of SleepView")
        self._view = view or SleepView()
        self.q_widget = self._view

        if controller is not None and not isinstance(controller, SleepController):
            raise TypeError("controller must be an instance of SleepController")
        self._controller = controller or SleepController(
            self._model,
            self._view,
            axis=axis,
            config_file=config_file,
        )
        self._apply_theme()
        install_action_shortcuts(self._view)
        if cfg.show_gui and getattr(QtCore, "QTimer", None) is not None:
            self._install_view_ready_handler()
            self._schedule_visual_initialization()
        else:
            self._controller.initialize_visuals_if_needed()

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------
    def initialize_visuals(self) -> None:
        """Ensure the underlying VisPy visuals are constructed."""

        self._controller.initialize_visuals_if_needed()

    def _schedule_visual_initialization(self, delay: int = 0) -> None:
        """Defer the visuals setup until the Qt event loop starts."""

        if self._visuals_timer_scheduled:
            return
        timer = getattr(QtCore, "QTimer", None)
        if timer is None:
            self._controller.initialize_visuals_if_needed()
            return
        self._visuals_timer_scheduled = True
        timer.singleShot(delay, self._initialize_visuals_when_ready)

    def _initialize_visuals_when_ready(self) -> None:
        """Retry until the backing Qt window is visible and exposed."""

        self._visuals_timer_scheduled = False
        app_cls = getattr(QtWidgets, "QApplication", None)
        if callable(getattr(app_cls, "instance", None)):
            instance = app_cls.instance()
            if instance is not None:
                loop_cls = getattr(QtCore, "QEventLoop", None)
                loop_flag = getattr(loop_cls, "AllEvents", None) if loop_cls else None
                if loop_flag is not None:
                    instance.processEvents(loop_flag, 50)
        window = getattr(self._view, "windowHandle", None)
        window_handle = window() if callable(window) else None
        visible = bool(getattr(self._view, "isVisible", lambda: True)())
        exposed = True
        if window_handle is not None:
            exposed = bool(getattr(window_handle, "isExposed", lambda: True)())

        if not visible or not exposed:
            self._visual_retry_count += 1
            if self._visual_retry_count <= 50:
                self._schedule_visual_initialization(delay=20)
                return
        self._visual_retry_count = 0
        self._controller.initialize_visuals_if_needed()

    def _install_view_ready_handler(self) -> None:
        """Install an event filter that fires when the window becomes visible."""

        if getattr(QtCore, "QObject", None) is None:
            return

        class _ViewReadyFilter(QtCore.QObject):
            def __init__(self, view, callback):
                super().__init__(view)
                self._view = view
                self._callback = callback
                self._armed = True

            def eventFilter(self, obj, event):
                if not self._armed or obj is not self._view:
                    return super().eventFilter(obj, event)

                etype = event.type()
                event_names = [
                    "Show",
                    "ShowToParent",
                    "WindowActivate",
                    "Expose",
                    "UpdateRequest",
                ]
                interesting = {
                    getattr(QtCore.QEvent, name)
                    for name in event_names
                    if hasattr(QtCore.QEvent, name)
                }
                if etype not in interesting:
                    return super().eventFilter(obj, event)

                view = self._view
                handle = None
                window_handle = getattr(view, "windowHandle", None)
                if callable(window_handle):
                    handle = window_handle()
                if handle is None and hasattr(view, "createWinId"):
                    try:
                        view.createWinId()
                        if callable(window_handle):
                            handle = window_handle()
                    except Exception:
                        handle = None

                visible = bool(getattr(view, "isVisible", lambda: True)())
                exposed = True
                if handle is not None and hasattr(handle, "isExposed"):
                    exposed = bool(handle.isExposed())

                if visible and exposed:
                    self._armed = False
                    QtCore.QTimer.singleShot(0, self._callback)

                return super().eventFilter(obj, event)

        def _on_ready():
            if self._view_ready_filter is not None:
                self._view.removeEventFilter(self._view_ready_filter)
                self._view_ready_filter = None
            self.initialize_visuals()

        self._view_ready_filter = _ViewReadyFilter(self._view, _on_ready)
        self._view.installEventFilter(self._view_ready_filter)

    # ------------------------------------------------------------------
    # Composition accessors
    # ------------------------------------------------------------------
    @property
    def controller(self) -> SleepController:
        return self._controller

    @property
    def view(self) -> SleepView:
        return self._view

    @property
    def model(self) -> SleepDataset:
        return self._model

    # ------------------------------------------------------------------
    # Delegation helpers
    # ------------------------------------------------------------------
    def __getattr__(self, name):
        try:
            return getattr(self._controller, name)
        except AttributeError:
            try:
                return getattr(self._view, name)
            except AttributeError as err:
                raise AttributeError(name) from err

    # ------------------------------------------------------------------
    # Basic collection protocol
    # ------------------------------------------------------------------
    def __len__(self):
        return len(self._controller)

    def __getitem__(self, key):
        return self._controller[key]

    # ------------------------------------------------------------------
    # Public API proxies
    # ------------------------------------------------------------------
    def replace_detections(self, dtype, method):
        return self._controller.replace_detections(dtype, method)
