"""Main class for sleep tools managment."""


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

        # =====================================================================
        # FILTERING
        # =====================================================================
        self._SigFiltApply.clicked.connect(self._fcn_sigProcessing)
        self._SigFilt.clicked.connect(self._fcn_filtViz)
        self._SigFiltBand.currentIndexChanged.connect(self._fcn_filtBand)

    # =====================================================================
    # DEMEAN / DETREND / FILTERING
    # =====================================================================
    def _fcn_sigProcessing(self):
        """Signal processing function."""
        # ========== VALUES ==========
        # Mean and trend :
        demean = self._SigMean.isChecked()
        detrend = self._SigTrend.isChecked()
        # Filtering :
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
