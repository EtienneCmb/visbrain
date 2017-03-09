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
        self._SigMean.clicked.connect(self._fcn_sigProcessing)
        self._SigTrend.clicked.connect(self._fcn_sigProcessing)
        self._SigFiltApply.clicked.connect(self._fcn_sigProcessing)
        self._SigFilt.clicked.connect(self._fcn_filtViz)
        self._SigFiltBand.currentIndexChanged.connect(self._fcn_filtBand)

        # =====================================================================
        # FILTERING
        # =====================================================================

        # =====================================================================
        # REM / SPINDLES / DETECTION
        # =====================================================================
        # Commonth elements :
        self._ToolDetecVisible.clicked.connect(self._fcn_detectViz)
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
        self._ToolSpinTh.setValue(3.)

    # =====================================================================
    # DEMEAN / DETREND / FILTERING
    # =====================================================================
    def _fcn_sigProcessing(self):
        """Signal processing function."""
        # ========== VALUES ==========
        # Mean and trend :
        demean = self._SigMean.isChecked()
        detrend = self._SigTrend.isChecked()
        # Filetring :
        filt = self._SigFilt.isChecked()
        fstart = self._SigFiltFrom.value()
        fend = self._SigFiltTo.value()
        filttype = self._SigFiltMeth.currentText()
        filtorder = self._SigFiltOrder.value()
        filtband = self._SigFiltBand.currentText()

        # ========== CHANNELS ==========
        # ---- Demean / detrend ----
        self._chan.demean = demean
        self._chan.detrend = detrend
        # ---- Filtering ----
        self._chan.filt = filt
        self._chan.fstart = fstart
        self._chan.fend = fend
        self._chan.forder = filtorder
        self._chan.filt_type = filttype
        self._chan.filt_band = filtband

        self._chan.update()

        # ========== SPECTROGRAM ==========
        # ---- Demean / detrend ----
        self._spec.demean = demean
        self._spec.detrend = detrend
        # ---- Filtering ----
        self._spec.filt = filt
        self._spec.filt = filt
        self._spec.fstart = fstart
        self._spec.fend = fend
        self._spec.forder = filtorder
        self._spec.filt_type = filttype
        self._spec.filt_band = filtband

        self._spec.update()

    def _fcn_filtViz(self):
        """Display / hide filtering panel."""
        viz = self._SigFilt.isChecked()
        self._SigFiltW.setEnabled(viz)
        if not viz:
            self._fcn_sigProcessing()

    def _fcn_filtBand(self):
        """Configure visible [fstart, fend] for the band possibilities."""
        # Get selected band :
        filtband = self._SigFiltBand.currentText()
        # Enable / disable [fstart, fend] :
        if filtband in ['bandpass', 'bandstop']:
            fstart, fend = True, True
        elif filtband == 'lowpass':
            fstart, fend = False, True
        elif filtband == 'highpass':
            fstart, fend = True, False
        # Set enable fstart / fend :
        self._SigFiltFrom.setEnabled(fstart)
        self._SigFiltTo.setEnabled(fend)

    # =====================================================================
    # DETECTION
    # =====================================================================
    def _fcn_detectViz(self):
        """Toggle vivibility of detections."""
        # Get button state :
        viz = self._ToolDetecVisible.isChecked()
        # Turn all detected lines / markers to viz :
        for k in range(len(self)):
            # Toggle lines (for REM and spindles) :
            self._chan.report[k].visible = viz
            # Toggle markers (for peaks) :
            self._chan.peak[k].visible = viz
        # Hypnogram :
        self._hyp.report.visible = viz

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

            # Get if report is enable and checked:
            toReport = self._ToolDetecReport.isEnabled(
                                       ) and self._ToolDetecReport.isChecked()

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
                if toReport:
                    self._hyp.set_report(self._time, index, color='slateblue',
                                         symbol='triangle_down',
                                         y=-self._hypno[index]+.2)

            # ------------------- SPINDLES -------------------
            elif method == 'Spindles':
                # Get variables :
                thr = self._ToolSpinTh.value()
                # Get Spindles indices :
                index, _, _ = spindlesdetect(self._data[k, :], self._sf, thr,
                                             self._hypno)
                # Set them to ChannelPlot object :
                self._chan.colidx[k] = index
                # Report index on hypnogram :
                if toReport:
                    self._hyp.set_report(self._time, index, color='olive',
                                         symbol='x', y=-self._hypno[index]+.2)

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
                if toReport:
                    self._hyp.set_report(self._time, self._peak.index,
                                         color='firebrick', symbol='vbar',
                                         y=-self._hypno[self._peak.index]+.2)
            # Be sure panel is displayed :
            if not self.canvas_isVisible(k):
                self.canvas_setVisible(k, True)
                self._chan.visible[k] = True

            # Update plot :
            self._fcn_sliderMove()

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
        viz = self._ToolRdSelected.isChecked()
        self._ToolDetecReport.setEnabled(viz)
        self._ToolDetectChan.setEnabled(viz)
