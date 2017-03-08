"""Main class for sleep tools managment."""

from ....utils import remdetect, spindlesdetect

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
        # REM / SPINDLES / DETECTION
        # =====================================================================
        # Commonth elements :
        self._ToolDetectChan.addItems(self._channels)
        self._ToolDetectType.currentIndexChanged.connect(
                                                     self._fcn_switchDetection)
        self._ToolDetectApply.clicked.connect(self._fcn_applyDetection)
        self._fcn_switchDetection()

        # -------------------------------------------------
        # REM detection :
        self._ToolRemTh.setValue(3.)

        # -------------------------------------------------
        # Spindles detection :
        self._ToolSpinTh.setValue(4.)

    # =====================================================================
    # DETECTION
    # =====================================================================
    def _fcn_switchDetection(self):
        """Switch between detection types (show / hide panels)."""
        # Define ref :
        ref = ['REM', 'Spindles', 'Peaks']
        # Get current selected text :
        viz = [self._ToolDetectType.currentText() == k for k in ref]
        # Set widget visibility :
        _ = [k.setVisible(i) for k, i in zip([self._ToolRemPanel,
                                             self._ToolSpinPanel,
                                             self._ToolPeakPanel], viz)]

    def _fcn_applyDetection(self):
        """Apply detection (either REM / Spindles / Peaks."""
        # Get current channel and detection method :
        idx = self._ToolDetectChan.currentIndex()
        method = self._ToolDetectType.currentText()

        # Switch between detection types :
        # ------------------- REM -------------------
        if method == 'REM':
            # Get variables :
            thr = self._ToolRemTh.value()
            # Get REM indices :
            index, _, _ = remdetect(self._data[idx, :], self._sf, thr)
            # Set them to ChannelPlot object :
            self._chan.colidx[idx] = index
            # Update plot :
            self._fcn_sliderMove()

        # ------------------- SPINDLES -------------------
        elif method == 'Spindles':
            # Get variables :
            thr = self._ToolSpinTh.value()
            # Get Spindles indices :
            index, _, _ = spindlesdetect(self._data[idx, :], self._sf, thr)
            # Set them to ChannelPlot object :
            self._chan.colidx[idx] = index
            # Update plot :
            self._fcn_sliderMove()

        # ------------------- PEAKS -------------------
        elif method == 'Peaks':
            # Get variables :
            look = self._ToolPeakLook.value()
            disp = self._ToolPeakMinMax.currentIndex()
            disp_types = ['max', 'min', 'minmax']
            # Set data :
            self._peak.set_data(self._data[idx], self._time,
                                self._chan.peak[idx], disp_types[disp], look)

        # Be sure panel is displayed :
        if not self.canvas_isVisible(idx):
            self.canvas_setVisible(idx, True)
