"""Top-level Sleep façade assembling model, view and controller."""

from __future__ import annotations

from typing import Optional

from visbrain._pyqt_module import _PyQtModule
from visbrain.config import PROFILER, ensure_qt_app
from visbrain.gui._accessibility import install_action_shortcuts

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
