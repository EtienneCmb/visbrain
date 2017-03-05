"""Main class for settings managment."""


__all__ = ['uiTools']


class uiTools(object):
    """Main class for settings managment."""

    def __init__(self):
        """Init."""
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
        self._peak.set_data(self._data[idx], self._time, disp_types[disp],
                            look, self._chanCanvas[idx].wc.scene)
        if not self.canvas_isVisible(idx):
            self.canvas_setVisible(idx, True)
