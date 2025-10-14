"""Controller coordinating Sleep model and view interactions."""

from __future__ import annotations

import logging
from concurrent.futures import Future

import numpy as np

from visbrain.config import PROFILER
from visbrain.gui.threading import invoke_in_gui_thread
from visbrain.utils import MouseEventControl, color2vb

from .interface import UiElements
from .loader import AsyncSleepLoader
from .model import SleepDataset
from .visuals import Visuals


class SleepController(UiElements, Visuals, MouseEventControl):
    """Encapsulate business logic for the Sleep GUI."""

    _logger = logging.getLogger("visbrain")

    def __init__(self, model, view, *, axis=True, config_file=None):
        object.__setattr__(self, "_model", model)
        object.__setattr__(self, "_view", view)

        # -------------------- GUI state --------------------
        self._config_file = config_file
        self._annot_mark = np.array([])
        self._ax = axis
        self._async_loader = AsyncSleepLoader()

        # Default rendering parameters
        self._lw = 1.0
        self._lwhyp = 2
        self._defwin = 30.0
        self._defstd = 5.0
        self._chancolor = '#292824'
        self._hypcolor = {
            -1: '#8bbf56',
            0: '#56bf8b',
            1: '#aabcce',
            2: '#405c79',
            3: '#0b1c2c',
            4: '#bf5656',
        }
        self._indicol = '#e74c3c'
        self._defcmap = 'viridis'
        self._defspin = color2vb('#d73737')
        self._defsw = color2vb('#56bf8b')
        self._defkc = color2vb('#b45a3c')
        self._defrem = color2vb('#6684e1')
        self._defmt = color2vb('#FE8625')
        self._defpeaks = '#b854d4'
        self._spinsym = 'x'
        self._swsym = 'o'
        self._kcsym = 'diamond'
        self._remsym = 'triangle_down'
        self._mtsym = 'star'
        self._peaksym = 'disc'

        view.set_default_state()

        MouseEventControl.__init__(self)

        # Harmonize hypnogram colors with conversion tables
        hconvinv = self._model.hconvinv
        if self._model.hconv != hconvinv:
            hypc = self._hypcolor.copy()
            for key in self._model.hconv.keys():
                self._hypcolor[key] = hypc[hconvinv[key]]

        self._get_data_info()
        PROFILER("Data info")

        PROFILER("Initialize GUI interactions", as_type='title')
        UiElements.__init__(self)

        for attr in (
            '_chanCanvas',
            '_specCanvas',
            '_hypCanvas',
            '_topoCanvas',
            '_TimeAxis',
        ):
            setattr(self._view, attr, getattr(self, attr))

        view.create_cameras(len(self))
        self._visuals_initialized = False
        self._initializing_visuals = False

    # ------------------------------------------------------------------
    # Delegation helpers
    # ------------------------------------------------------------------
    def __getattr__(self, name):
        try:
            return getattr(self._view, name)
        except AttributeError as err:
            raise AttributeError(name) from err

    # ------------------------------------------------------------------
    # Model proxies
    # ------------------------------------------------------------------
    def __len__(self):
        return len(self._model)

    def __getitem__(self, key):
        return self._model[key]

    @property
    def _data(self):
        return self._model.data

    @_data.setter
    def _data(self, value):
        self._model.data = value

    @property
    def _hypno(self):
        return self._model.hypno

    @_hypno.setter
    def _hypno(self, value):
        self._model.hypno = value

    @property
    def _time(self):
        return self._model.time

    @_time.setter
    def _time(self, value):
        self._model.time = value

    @property
    def _channels(self):
        return self._model.channels

    @_channels.setter
    def _channels(self, value):
        self._model.channels = value

    @property
    def _href(self):
        return self._model.href

    @_href.setter
    def _href(self, value):
        self._model.href = value

    @property
    def _hconv(self):
        return self._model.hconv

    @_hconv.setter
    def _hconv(self, value):
        self._model.hconv = value

    @property
    def _hconvinv(self):
        return self._model.hconvinv

    @property
    def _sf(self):
        return self._model.sf

    @_sf.setter
    def _sf(self, value):
        self._model.sf = value

    @property
    def _sfori(self):
        return self._model.sfori

    @_sfori.setter
    def _sfori(self, value):
        self._model.sfori = value

    @property
    def _dsf(self):
        return self._model.dsf

    @_dsf.setter
    def _dsf(self, value):
        self._model.dsf = value

    @property
    def _N(self):
        return self._model.n_points

    @_N.setter
    def _N(self, value):
        self._model.n_points = value

    @property
    def _file(self):
        return self._model.file

    @_file.setter
    def _file(self, value):
        self._model.file = value

    @property
    def _annot_file(self):
        return self._model.annotations

    @_annot_file.setter
    def _annot_file(self, value):
        self._model.annotations = value

    @property
    def _datainfo(self):
        return self._model.datainfo

    @_datainfo.setter
    def _datainfo(self, value):
        self._model.datainfo = value

    @property
    def _custom_detections(self):
        return self._model.custom_detections

    # ------------------------------------------------------------------
    # Asynchronous loading
    # ------------------------------------------------------------------
    def load_dataset_async(
        self,
        *,
        data=None,
        channels=None,
        sf=None,
        hypno=None,
        href=None,
        preload=None,
        use_mne=None,
        downsample=None,
        kwargs_mne=None,
        annotations=None,
    ):
        """Load a dataset in the background and hydrate the existing model."""

        if href is None:
            href = list(self._model.href)
        if channels is None:
            channels = list(self._model.channels)
        if sf is None:
            sf = float(self._model.sfori)
        if preload is None:
            preload = True
        if use_mne is None:
            use_mne = False
        if downsample is None:
            downsample = float(self._model.sf)
        if kwargs_mne is None:
            kwargs_mne = {}
        else:
            kwargs_mne = dict(kwargs_mne)

        future = self._async_loader.submit(
            SleepDataset,
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

        def _dispatch(done: Future) -> None:
            try:
                dataset = done.result()
            except BaseException as exc:  # pragma: no cover - defensive
                self._logger.error("Asynchronous sleep load failed", exc_info=exc)
                return
            invoke_in_gui_thread(self._hydrate_from_dataset, dataset)

        future.add_done_callback(_dispatch)
        return future

    def _hydrate_from_dataset(self, dataset: SleepDataset) -> None:
        """Populate the current model with arrays from *dataset*."""

        self._model.data = np.array(dataset.data, copy=True)
        self._model.hypno = np.array(dataset.hypno, copy=True)
        self._model.time = np.array(dataset.time, copy=True)
        self._model.channels = list(dataset.channels)
        self._model.href = list(dataset.href)
        self._model.hconv = dict(dataset.hconv)
        self._model.sf = float(dataset.sf)
        self._model.sfori = float(dataset.sfori)
        self._model.dsf = int(dataset.dsf)
        self._model.n_points = int(dataset.n_points)
        self._model.file = dataset.file
        self._model.annotations = np.array(dataset.annotations, copy=True)
        self._get_data_info()

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------
    def _get_data_info(self):
        return self._model.refresh_data_info()

    def initialize_visuals_if_needed(self) -> None:
        """Create the VisPy visuals once the Qt window is ready."""

        if self._visuals_initialized or self._initializing_visuals:
            return

        self._initializing_visuals = True
        try:
            PROFILER("Initialize visual elements", as_type='title')
            Visuals.__init__(self)
        except Exception:
            self._visuals_initialized = False
            raise
        else:
            self._visuals_initialized = True
            self._fcns_on_creation()
            PROFILER("Functions on creation")
        finally:
            self._initializing_visuals = False

    def _fcns_on_creation(self):
        self._fcn_grid_toggle()
        self._fcn_scorwin_indicator_toggle()
        self._fcn_sigwin_settings()
        self._fcn_slider_move()
        self._chanChecks[0].setChecked(True)
        self._hypLabel.setVisible(self.menuDispHypno.isChecked())
        self._fcn_chan_viz()
        self._fcn_chan_sym_amp()
        self._fcn_info_update()
        self._fcn_hypno_to_score()
        self._SpecW.setVisible(True)
        self._HypW.setVisible(True)
        self._TimeAxisW.setVisible(True)
        if self._config_file is not None:
            self._load_config(filename=self._config_file)
        if self._annot_file is not None:
            self._load_annotation_table(filename=self._annot_file)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def replace_detections(self, dtype, method):
        meth_names = ('spindle', 'sw', 'kc', 'rem', 'mt', 'peak')
        if dtype not in meth_names:
            raise ValueError(
                "dtype should be a string. Choose between %s" % ', '.join(meth_names)
            )
        if not hasattr(method, '__call__'):
            raise AssertionError("method must be callable")
        self._model.replace_detection(dtype, method)
        self._fcn_switch_detection()
