"""Top level Sleep class."""
import numpy as np

import vispy.scene.cameras as viscam

from .interface import UiInit, UiElements
from .visuals import Visuals
from ..pyqt_module import PyQtModule
from ..utils import (FixedCam, color2vb, MouseEventControl)
from ..io import ReadSleepData
from ..config import PROFILER


class Sleep(PyQtModule, ReadSleepData, UiInit, Visuals, UiElements,
            MouseEventControl):
    """Visualize and edit sleep data.

    Use this module to :

        * Load and visualize polysomnographic data and spectrogram.
        * Load, edit and save hypnogram from the interface
        * Perform automatic events detection
        * Further signal processing tools (de-mean, de-trend and filtering)
        * Topographic data visualization

    Sleep has been developped in collaboration with Raphael Vallat.

    Parameters
    ----------
    data : string, array_like | None
        Polysomnographic data. Must either be a path to a supported file (see
        notes) or an array of raw data of shape (n_channels, n_pts). If None,
        a dialog window to load the file should appear.
    hypno : array_like | None
        Hypnogram data. Should be a raw vector of shape (n_pts,)
    config_file : string | None
        Path to the configuration file (.txt)
    annotations : string | None
        Path to the annotation file (.txt, .csv). Alternatively, you can pass
        an annotation instance of MNE or simply an (N,) array describing
        the onset.
    channels : list | None
        List of channel names. The length of this list must be n_channels.
    sf : float | None
        The sampling frequency of raw data.
    downsample : float | 100.
        The downsampling frequency for the data and hypnogram raw data.
    axis : bool | False
        Specify if each axis have to contains its own axis. Be carefull
        with this option, the rendering can be much slower.
    href : list | ['art', 'wake', 'rem', 'n1', 'n2', 'n3']
        List of sleep stages. This list can be used to changed the display
        order into the GUI.
    preload : bool | True
        Preload data into memory. For large datasets, turn this parameter to
        True.
    use_mne : bool | False
        Force to load the file using mne.io functions.
    kwargs_mne : dict | {}
        Dictionary to pass to the mne.io loading function.

    Notes
    -----
    .. note::
        * Supported polysomnographic files : by default, Sleep support .vhdr
          (BrainVision), .eeg (Elan), .trc (Micromed) and .edf (European Data
          Format). If mne-python is installed, this default list of supported
          files is extended to .cnt, .egi, .mff, .edf, .bdf, .gdf, .set, .vhdr.
        * Supported hypnogram files : by default, Sleep support .txt, .csv and
          .hyp hypnogram files.

    .. deprecated:: 0.3.4
        Input arguments `file` and `hypno_file` has been deprecated in 0.3.4
        release. Use instead the `data` and `hypno` inputs.
    """

    def __init__(self, data=None, hypno=None, config_file=None,
                 annotations=None, channels=None, sf=None, downsample=100.,
                 axis=True, href=['art', 'wake', 'rem', 'n1', 'n2', 'n3'],
                 preload=True, use_mne=False, kwargs_mne={}, verbose=None):
        """Init."""
        PyQtModule.__init__(self, verbose=verbose, icon='sleep_icon.svg')
        # ====================== APP CREATION ======================
        UiInit.__init__(self)

        # Set default GUI state :
        self._set_default_state()

        # Mouse control :
        MouseEventControl.__init__(self)

        # ====================== LOAD FILE ======================
        PROFILER("Import file", as_type='title')
        ReadSleepData.__init__(self, data, channels, sf, hypno, href, preload,
                               use_mne, downsample, kwargs_mne,
                               annotations)

        # ====================== VARIABLES ======================
        # Check all data :
        self._config_file = config_file
        self._annot_mark = np.array([])
        self._hconvinv = {v: k for k, v in self._hconv.items()}
        self._ax = axis
        # ---------- Default line width ----------
        self._lw = 1.
        self._lwhyp = 2
        self._defwin = 30.
        self._defstd = 5.
        # ---------- Default colors ----------
        self._chancolor = '#292824'
        # self._hypcolor = '#292824'
        # Hypnogram color :
        self._hypcolor = {-1: '#8bbf56', 0: '#56bf8b', 1: '#aabcce',
                          2: '#405c79', 3: '#0b1c2c', 4: '#bf5656'}
        # Convert color :
        if self._hconv != self._hconvinv:
            hypc = self._hypcolor.copy()
            for k in self._hconv.keys():
                self._hypcolor[k] = hypc[self._hconvinv[k]]
        self._indicol = '#e74c3c'
        # Default spectrogram colormap :
        self._defcmap = 'viridis'
        # Spindles / REM / Peaks colors :
        self._defspin = color2vb('#d73737')
        self._defsw = color2vb('#56bf8b')
        self._defkc = color2vb('#b45a3c')
        self._defrem = color2vb('#6684e1')
        self._defmt = color2vb('#FE8625')
        self._defpeaks = '#b854d4'
        # ---------- Symbol ----------
        self._spinsym = 'x'
        self._swsym = 'o'
        self._kcsym = 'diamond'
        self._remsym = 'triangle_down'
        self._mtsym = 'star'
        self._peaksym = 'disc'
        # Get some data info (min / max / std / mean)
        self._get_data_info()
        PROFILER("Data info")

        # ====================== USER & GUI INTERACTION  ======================
        # User <-> GUI :
        PROFILER("Initialize GUI interactions", as_type='title')
        UiElements.__init__(self)

        # ====================== CAMERAS ======================
        self._cam_creation()

        # ====================== OBJECTS CREATION ======================
        PROFILER("Initialize visual elements", as_type='title')
        Visuals.__init__(self)

        # ====================== FUNCTIONS ON LOAD ======================
        self._fcns_on_creation()
        PROFILER("Functions on creation")

    def __len__(self):
        """Return the number of channels."""
        return len(self._channels)

    def __getitem__(self, key):
        """Return corresponding data info."""
        return self._datainfo[key]

    ###########################################################################
    # SUB-FONCTIONS
    ###########################################################################
    def _get_data_info(self):
        """Get some info about data (min, max, std, mean, dist)."""
        self._datainfo = {'min': self._data.min(1), 'max': self._data.max(1),
                          'std': self._data.std(1), 'mean': self._data.mean(1),
                          'dist': self._data.max(1) - self._data.min(1)}

    def _set_default_state(self):
        """Set the default window state."""
        # ================= TAB =================
        self._DetectionTab.setCurrentIndex(0)
        self._stacked_panels.setCurrentIndex(0)
        self._stacked_tools.setCurrentIndex(0)
        self._stacked_detections.setCurrentIndex(0)

    def _cam_creation(self):
        """Create a set of cameras."""
        # ------------------- Channels -------------------
        self._chanCam = []
        for k in range(len(self)):
            self._chanCam.append(FixedCam())  # viscam.PanZoomCamera()
        # ------------------- Spectrogram -------------------
        self._speccam = FixedCam()  # viscam.PanZoomCamera()
        self._specCanvas.set_camera(self._speccam)
        # ------------------- Hypnogram -------------------
        self._hypcam = FixedCam()  # viscam.PanZoomCamera()
        self._hypCanvas.set_camera(self._hypcam)
        # ------------------- Topoplot -------------------
        self._topocam = viscam.PanZoomCamera()
        self._topoCanvas.set_camera(self._topocam)
        # ------------------- Time axis -------------------
        self._timecam = FixedCam()
        self._TimeAxis.set_camera(self._timecam)

        # Keep all cams :
        self._allCams = (self._chanCam, self._speccam, self._hypcam,
                         self._topocam, self._timecam)

    def _fcns_on_creation(self):
        """Applied on creation."""
        self._fcn_grid_toggle()
        self._fcn_slider_move()
        self._chanChecks[0].setChecked(True)
        self._hypLabel.setVisible(self.menuDispHypno.isChecked())
        self._fcn_chan_viz()
        self._fcn_chan_sym_amp()
        self._fcn_info_update()
        self._fcn_hypno_to_score()
        # Set objects visible :
        self._SpecW.setVisible(True)
        self._HypW.setVisible(True)
        self._TimeAxisW.setVisible(True)
        # File to load :
        if self._config_file is not None:  # Config file
            self._load_config(filename=self._config_file)
        if self._annot_file is not None:   # Annotation file
            self._load_annotation_table(filename=self._annot_file)
