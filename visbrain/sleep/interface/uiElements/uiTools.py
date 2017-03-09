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
        # Apply method (Selected / Visible / All) :
        self._ToolRdSelected.clicked.connect(self._fcn_applyMethod)
        self._ToolRdViz.clicked.connect(self._fcn_applyMethod)
        self._ToolRdAll.clicked.connect(self._fcn_applyMethod)
        self._ToolDetectProgress.hide()
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
        # Get channels to apply detection and the detection method :
        idx = self._fcn_getChanDetection()
        method = self._ToolDetectType.currentText()

        for i, k in enumerate(idx):
            # Display progress bar :
            self._ToolDetectProgress.show()

            # Switch between detection types :
            # ------------------- REM -------------------
            if method == 'REM':
                # Get variables :
                thr = self._ToolRemTh.value()
                # Get REM indices :
                index, _, _ = remdetect(self._data[k, :], self._sf, thr)
                # Set them to ChannelPlot object :
                self._chan.colidx[k] = index
                # Report index on hypnogram :
                if self._ToolDetecReport.isEnabled():
                    self._hyp.set_report(self._time, index, color='slateblue',
                                         symbol='triangle_down',
                                         y=-self._hypno[index]+.2)
                # Update plot :
                self._fcn_sliderMove()

            # ------------------- SPINDLES -------------------
            elif method == 'Spindles':
                # Get variables :
                thr = self._ToolSpinTh.value()
                # Get Spindles indices :
                index, _, _ = spindlesdetect(self._data[k, :], self._sf, thr)
                # Set them to ChannelPlot object :
                self._chan.colidx[k] = index
                # Report index on hypnogram :
                if self._ToolDetecReport.isEnabled():
                    self._hyp.set_report(self._time, index, color='olive',
                                         symbol='x', y=-self._hypno[index]+.2)
                # Update plot :
                self._fcn_sliderMove()

            # ------------------- PEAKS -------------------
            elif method == 'Peaks':
                # Get variables :
                look = self._ToolPeakLook.value() * self._sf
                disp = self._ToolPeakMinMax.currentIndex()
                disp_types = ['max', 'min', 'minmax']
                # Set data :
                self._peak.set_data(self._sf, self._data[k], self._time,
                                    self._chan.peak[k], disp_types[disp],
                                    look)
                # Report index on hypnogram :
                if self._ToolDetecReport.isEnabled():
                    self._hyp.set_report(self._time, self._peak.index,
                                         color='firebrick', symbol='vbar',
                                         y=-self._hypno[self._peak.index]+.2)
            # Be sure panel is displayed :
            if not self.canvas_isVisible(k):
                self.canvas_setVisible(k, True)

            # Update progress bar :
            self._ToolDetectProgress.setValue(100. * (i + 1) / len(self))

        # Finally, hide progress bar :
        self._ToolDetectProgress.hide()

    def _fcn_getChanDetection(self):
        """Get on which channel to apply the detection."""
        # Selected channel :
        if self._ToolRdSelected.isChecked():
            idx = [self._ToolDetectChan.currentIndex()]

        # Visible channels :
        elif self._ToolRdViz.isChecked():
            idx = [
                k for k in range(len(self)) if self._chanWidget[k].isVisible()]

        # All channels :
        elif self._ToolRdAll.isChecked():
            idx = range(len(self))

        return idx

    def _fcn_applyMethod(self):
        """Be sure to apply hypnogram report only on selected channel."""
        self._ToolDetecReport.setEnabled(self._ToolRdSelected.isChecked())
