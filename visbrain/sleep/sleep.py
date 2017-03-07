"""Top level Sleep class."""
import numpy as np

from PyQt4 import QtGui
import sys
from warnings import warn

import vispy.app as visapp
import vispy.scene.cameras as viscam

from .interface import uiInit, uiElements
from .visuals import visuals
from .tools import Tools
from ..utils import FixedCam, load_sleepdataset, load_hypno
# from .user import userfcn


class Sleep(uiInit, visuals, uiElements, Tools):
    """One line description.

    Multiple lines description...
    """

    def __init__(self, file=None, hypno_file=None, data=None, channels=None,
                 sf=None, hypno=None, downsample=200, axis=False, line='gl'):
        """Init."""
        # ====================== APP CREATION ======================
        # Create the app and initialize all graphical elements :
        self._app = QtGui.QApplication(sys.argv)
        uiInit.__init__(self)

        # ====================== LOAD FILE ======================
        # Load file and convert if needed :
        if not all([k is not None for k in [data, channels, sf]]):
            # --------------- Qt Dialog ---------------
            if (file is None) or not isinstance(file, str):
                # Dialog window for the main dataset :
                file = QtGui.QFileDialog.getOpenFileName(
                        self, "Open dataset", "", "Elan (*.eeg);;"
                        "Brainvision (*.eeg);;Edf (*.edf)")
                # Load hypnogram :
                hypno_file = QtGui.QFileDialog.getOpenFileName(
                        self, "Open hypnogram", "", "Elan (*.hyp);;"
                        "Text file (*.txt);;""CSV file (*.csv)")

            # Load dataset :
            if downsample:
                # Apply a specific downsampling (Elan only)
                sf, data, channels = load_sleepdataset(file, downsample)
            else:
                # Default: Apply 100 Hz downsampling (Elan only)
                sf, data, channels = load_sleepdataset(file)

            if hypno_file:
                # Load hypnogram :
                hypno = load_hypno(hypno_file, sf)

        # Empty hypnogram :
        if hypno is None:
            self._HypW.setVisible(False)
            self._PanHypViz.setChecked(False)

        # ====================== VARIABLES ======================
        # Check all data :
        self._file = file
        self._sf, self._data, self._hypno, self._time = self._check_data(
            sf, data, channels, hypno, downsample)
        self._channels = [k.split('.')[0] for k in channels]
        self._lw = 1.2
        self._lwhyp = 2.
        self._ax = axis
        self._defwin = 30.
        # Color :
        self._chancolor = '#34495e'
        self._hypcolor = '#34495e'
        self._indicol = '#e74c3c'
        # Get some data info (min / max / std / mean)
        self._datainfo = {'min': self._data.min(1), 'max': self._data.max(1),
                          'std': self._data.std(1), 'mean': self._data.mean(1),
                          'dist': self._data.max(1) - self._data.min(1)}
        self._defstd = 5.

        # ====================== USER & GUI INTERACTION  ======================
        # User <-> GUI :
        uiElements.__init__(self)

        # ====================== CAMERAS ======================
        # ------------------- Channels -------------------
        self._chanCam = []
        for k in range(len(self)):
            self._chanCam.append(FixedCam())  # viscam.PanZoomCamera()
        # ------------------- Spectrogram -------------------
        self._specCam = FixedCam()  # viscam.PanZoomCamera()
        self._specCanvas.set_camera(self._specCam)
        # ------------------- Hypnogram -------------------
        self._hypcam = viscam.PanZoomCamera()  # FixedCam()
        self._hypCanvas.set_camera(self._hypcam)
        # ------------------- Time axis -------------------
        self._timecam = FixedCam()
        self._TimeAxis.set_camera(self._timecam)

        # Keep all cams :
        cams = (self._chanCam, self._specCam, self._hypcam, self._timecam)

        # ====================== OBJECTS CREATION ======================
        visuals.__init__(self, self._sf, self._data, self._time,
                         self._channels, self._hypno, cameras=cams,
                         method=line)
        self._timecam.rect = (0, 0, list(self._hyp.rect)[2], 1)

        # ====================== TOOLS ======================
        Tools.__init__(self)

        # Finally set data and first channel only visible:
        self._fcn_sliderMove()
        self._chanChecks[0].setChecked(True)
        self._hypLabel.setVisible(self._PanHypViz.isChecked())
        self._fcn_chanViz()
        self._fcn_chanAmplitude()
        self._fcn_infoUpdate()

        ########################################
        from .visuals import Markers
        import vispy

        pos = np.random.rand(100, 2)
        pos[:, 0] *= 1000
        m2 = vispy.scene.visuals.Markers(parent=self._hypCanvas.wc.scene)
        m2.set_data(pos=pos, face_color='green')
        m = Markers(parent=self._hypCanvas.wc.scene)
        pos[:, 0] += 500.
        m.set_data(pos=pos, face_color='red')



    def __len__(self):
        """Return the number of channels."""
        return len(self._channels)

    def __getitem__(self, key):
        """Return corresponding data info."""
        return self._datainfo[key]

    def _check_data(self, sf, data, channels, hypno=None, downsample=None):
        """Check data, hypnogram, channels and sample frequency after loading.

        Args:
            sf: float
                The sampling frequency.

            data: np.ndarray
                The data to use. Must be a (n_channels, n_pts) array.

            channel: list
                List of string where each element refer to a channel names.
                The length of this list must be n_channels.

        Kargs:
            hypno: np.ndarray, optional, (def: None)
                A row vector of shape (npts,) containing hypnogram values.
                If the hypnogram is None, this functions returns a row vector
                fill with zeros.

            downsample: float, optional, (def: None)
                The down-sampling frequency. If this variable is not None it
                will replace the sampling frequency.

        Returns:
            sf: float
                The sampling frequency

            data: np.ndarray
                The float 32 data with a shape of (n_channels, n_pts).

            hypno: np.ndarray
                The float 32 hypnogram with a shape of (npts,).

            time: np.ndarray
                The time vector with a shape of (npts,).
        """
        # ========================== CHECKING ==========================
        nchan = len(channels)
        # Check sampling frequency :
        if not isinstance(sf, (int, float)):
            raise ValueError("The sampling frequency must be a float number "
                             "(e.g. 1024., 512., etc)")
        sf = float(sf)
        # Check data shape and format to float32 :
        # data = np.atleast_2d(data)
        if data.ndim is not 2:
            raise ValueError("The data must be a 2D array")
        if data.shape[0] is not nchan:
            warn("Organize data array as (n_channels, n_time_points) is more "
                 "memory efficient")
            data = data.T
        npts = data.shape[1]
        # Channels checking :
        if nchan not in data.shape:
            raise ValueError("Incorrect data shape. The number of channels "
                             "("+str(nchan)+') can not be found.')
        # Check hypnogram and format to float32 :
        if hypno is None:
            hypno = np.zeros((npts,), dtype=np.float32)
        else:
            # Check hypno length :
            if len(hypno) != npts:
                if len(hypno) < npts:
                    # Classic bug in Elan hypnogram file where EEG data is
                    # slightly longer than hyp file
                    hypno = np.append(hypno,
                                      (-1 * np.zeros((npts-len(hypno), 1))))
                else:
                    raise ValueError("The length of the hypnogram \
                                     vector must be" + str(npts) +
                                     " (Currently : " + str(len(hypno)) + ".")
            # Check hypno values :
            if (hypno.min() < -1.) or (hypno.max() > 4):
                warn("\nHypnogram values must be comprised between -1 and 4 "
                     "(see Iber et al. 2007). Use:\n-1 -> Art (optional)\n 0 "
                     "-> Wake\n 1 -> N1\n 2 -> N2\n 3 -> N4\n 4 -> REM\nEmpty "
                     "hypnogram will be used instead")
                hypno = np.zeros((npts,), dtype=np.float32)
        # Define time vector :
        time = np.arange(npts, dtype=np.float32) / sf

        # ========================== DOWN-SAMPLING ==========================
        if isinstance(downsample, (int, float)):
            # Find frequency ratio :
            fratio = round(sf / downsample)
            # Select time, data and hypno points :
            data = data[:, ::fratio]
            time = time[::fratio]
            hypno = hypno[::fratio]
            # Replace sampling frequency :
            sf = float(downsample)

        # ========================== CONVERSION ==========================
        # Convert data and hypno to be contiguous and float 32 (for vispy):
        data = np.ascontiguousarray(data.astype(np.float32, copy=False))
        hypno = np.ascontiguousarray(hypno.astype(np.float32, copy=False))

        return sf, data, hypno, time

    def show(self):
        """Display the graphical user interface."""
        # This function has to be placed here (and not in the user.py script)
        self.showMaximized()
        visapp.run()
