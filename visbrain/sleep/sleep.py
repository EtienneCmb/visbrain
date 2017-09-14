"""Top level Sleep class."""
import numpy as np
import sip

from PyQt5 import QtGui, QtWidgets
import sys
import os

import vispy.app as visapp
import vispy.scene.cameras as viscam

from .interface import uiInit, uiElements
from .visuals import Visuals
from .tools import Tools
from ..utils import (FixedCam, color2vb, MouseEventControl, set_widget_size)
from ..io import ReadSleepData

sip.setdestroyonexit(False)


class Sleep(ReadSleepData, uiInit, Visuals, uiElements, Tools,
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
    annotation_file : string | None
        Path to the annotation file (.txt, .csv). Alternatively, you can pass
        an annotation instance of MNE.
    channels : list | None
        List of channel names. The length of this list must be n_channels.
    sf : float | None
        The sampling frequency of raw data.
    downsample : float | 100.
        The downsampling frequency for the data and hypnogram raw data.
    axis : bool | Fals
        Specify if each axis have to contains its own axis. Be carefull
        with this option, the rendering can be much slower.
    line : string | 'gl'
        Specify the line rendering. Use 'gl' for the default line (fast) or
        'agg' for smooth lines. This option might not works on some
        plateforms.
    hedit : bool | False
        Enable the drag and drop hypnogram edition.
    href : list | ['art', 'wake', 'rem', 'n1', 'n2', 'n3']
        List of sleep stages. This list can be used to changed the display
        order into the GUI.
    ..versionadded:: 0.3.4
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
        * Supported polysomnographic files : by default, Sleep support .eeg
          (BrainVision and Elan), .trc (Micromed) and .edf (European Data
          Format). If mne-python is installed, this default list of supported
          files is extended to .cnt, .egi, .mff, .edf and .bdf.
        * Supproted hypnogram files : by default, Sleep support .txt, .csv and
          .hyp hypnogram files.

    .. deprecated:: 0.3.4
        Input arguments `file` and `hypno_file` has been deprecated in 0.3.4
        release. Use instead the `data` and `hypno` inputs.
    """

    def __init__(self, data=None, hypno=None, config_file=None,
                 annotation_file=None, channels=None, sf=None,
                 downsample=100., axis=False, line='gl',
                 hedit=False, href=['art', 'wake', 'rem', 'n1', 'n2', 'n3'],
                 preload=True, use_mne=False, kwargs_mne={}):
        """Init."""
        # ====================== APP CREATION ======================
        # Create the app and initialize all graphical elements :
        self._app = QtWidgets.QApplication(sys.argv)
        uiInit.__init__(self)

        # Set default GUI state :
        self._set_default_state()

        # Mouse control :
        MouseEventControl.__init__(self)

        # ====================== LOAD FILE ======================
        ReadSleepData.__init__(self, data, channels, sf, hypno, href, preload,
                               use_mne, downsample, kwargs_mne)

        # ====================== VARIABLES ======================
        # Check all data :
        self._config_file = config_file
        self._annot_file = annotation_file
        self._annot_mark = np.array([])
        self._hconvinv = {v: k for k, v in self._hconv.items()}
        self._ax = axis
        self._enabhypedit = hedit
        # ---------- Default line width ----------
        self._linemeth = line
        self._lw = 1.
        self._lwhyp = 2.5
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

        # ====================== USER & GUI INTERACTION  ======================
        # User <-> GUI :
        uiElements.__init__(self)

        # ====================== CAMERAS ======================
        self._cam_creation()

        # ====================== OBJECTS CREATION ======================
        Visuals.__init__(self)

        # ====================== TOOLS ======================
        Tools.__init__(self)

        # ====================== FUNCTIONS ON LOAD ======================
        self._fcns_on_creation()

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
        set_widget_size(self._app, self.q_widget, 23)
        self.QuickSettings.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(1)
        self.toolBox_2.setCurrentIndex(0)
        self._DetectionTab.setCurrentIndex(0)

        # ================= ICON =================
        pathfile = sys.modules[__name__].__file__.split('sleep.py')[0]
        app_icon = QtGui.QIcon()
        app_icon.addFile(os.path.join(pathfile, 'sleep_icon.svg'))
        self.setWindowIcon(app_icon)

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
        self._fcn_sliderMove()
        self._chanChecks[0].setChecked(True)
        self._hypLabel.setVisible(self.menuDispHypno.isChecked())
        self._fcn_chanViz()
        self._fcn_chanSymAmp()
        self._fcn_infoUpdate()
        self._fcn_Hypno2Score()
        # Set objects visible :
        self._SpecW.setVisible(True)
        self._HypW.setVisible(True)
        self._TimeAxisW.setVisible(True)
        # File to load :
        if self._config_file is not None:  # Config file
            self.loadConfig(filename=self._config_file)
        if self._annot_file is not None:   # Annotation file
            self.loadAnnotationTable(filename=self._annot_file)

    def show(self):
        """Display the graphical user interface."""
        # This function has to be placed here (and not in the user.py script)
        self.showMaximized()
        visapp.run()
