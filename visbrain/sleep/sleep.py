"""Top level Sleep class."""
import numpy as np

from PyQt4 import QtGui
import sys
from warnings import warn

import vispy.app as visapp
# import vispy.scene.cameras as viscam

from .interface import uiInit, uiElements
from .visuals import visuals
# from ..utils import id
# from .user import userfcn


class Sleep(uiInit, visuals, uiElements):
    """One line description.

    Multiple lines description...
    """

    def __init__(self, file=None, data=None, channels=None, sf=None,
                 hypno=None, downsample=None):
        """Init."""
        # ====================== Load ======================
        # Load file and convert if needed :
        pass

        # ====================== Variables ======================
        self._sf, self._data, self._hypno, self._time = self._check_data(
            sf, data, channels, hypno, downsample)
        self._channels = list(channels)

        # ====================== App creation ======================
        # Create the app and initialize all graphical elements :
        self._app = QtGui.QApplication(sys.argv)
        uiInit.__init__(self)

        # ====================== Objects creation ======================
        visuals.__init__(self)

        # ====================== user & GUI interaction  ======================
        # User <-> GUI :
        uiElements.__init__(self)

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
        data = np.atleast_2d(data)
        if data.ndim is not 2:
            raise ValueError("The data must be a 2D array")
        if nchan not in data.shape:
            raise ValueError("Incorrect data shape. The number of channels "
                             "("+str(nchan)+') can not be found.')
        if data.shape[0] is not nchan:
            warn("Organize data array as (n_channels, n_time_points) is more "
                 "memory efficient")
            data = data.T
        npts = data.shape[1]
        # Check hypnogram and format to float32 :
        if hypno is None:
            hypno = np.zeros((npts,), dtype=np.float32)
        else:
            if len(hypno) != npts:
                raise ValueError("The length of the hypnogram vector must be"
                                 " "+str(npts)+".")
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
