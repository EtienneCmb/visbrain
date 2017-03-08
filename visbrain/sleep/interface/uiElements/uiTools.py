"""Main class for sleep tools managment."""

from ....utils import remdetect

__all__ = ['uiTools']


class uiTools(object):
    """Main class for sleep tools managment."""

    def __init__(self):
        """Init."""
        # =====================================================================
        # MEAN / TREND
        # =====================================================================

        # =====================================================================
        # FILTERING
        # =====================================================================

        # =====================================================================
        # PEAK DETECTION
        # =====================================================================
        # Add list of channels :
        self._ToolPeakChan.addItems(self._channels)
        # Connect functions :
        self._ToolPeakChan.currentIndexChanged.connect(self._fcn_peakdetect)
        self._ToolPeakLook.valueChanged.connect(self._fcn_peakdetect)
        self._ToolPeakLook.setKeyboardTracking(False)
        self._ToolPeakMinMax.currentIndexChanged.connect(self._fcn_peakdetect)

        # =====================================================================
        # REM DETECTION
        # =====================================================================
        # _ToolRemChan -> Channel list
        # _ToolRemTh -> Threshold
        
        # Add list of channels :
        self._ToolRemChan.addItems(self._channels)
        self._ToolRemTh.setValue(3.)
        # Connect functions
        self._ToolRemChan.currentIndexChanged.connect(self._fcn_remdetect)
        self._ToolRemTh.valueChanged.connect(self._fcn_remdetect)
        self._ToolRemTh.setKeyboardTracking(False)

    # =====================================================================
    # PEAK DETECTION
    # =====================================================================
    def _fcn_peakdetect(self):
        """Perform and display a peak detection on the specified channel."""
        # Get variables :
        idx = self._ToolPeakChan.currentIndex()
        look = self._ToolPeakLook.value()
        disp = self._ToolPeakMinMax.currentIndex()
        disp_types = ['max', 'min', 'minmax']
        # Set data :
        self._peak.set_data(self._data[idx], self._time, self._chan.peak[idx],
                            disp_types[disp], look)
        if not self.canvas_isVisible(idx):
            self.canvas_setVisible(idx, True)

    # =====================================================================
    # REM DETECTION
    # =====================================================================
    def _fcn_remdetect(self):
        """Perform and display a rem detection on the specified channel."""
        # Get variables :
        idx = self._ToolRemChan.currentIndex()
        thr = self._ToolRemTh.value()
        # Set data
        if not self.canvas_isVisible(idx):
            self.canvas_setVisible(idx, True)
                