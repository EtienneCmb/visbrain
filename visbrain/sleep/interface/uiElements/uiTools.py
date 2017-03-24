"""Main class for sleep tools managment."""

import numpy as np
import gc

__all__ = ['uiTools']


class uiTools(object):
    """Main class for sleep tools managment."""

    def __init__(self):
        """Init."""
        # =====================================================================
        # RE-REFERENCING
        # =====================================================================
        self._ToolsRefLst.addItems(self._channels)
        self._ToolsRefSingle.clicked.connect(self._fcn_refPanelDisp)
        self._ToolsRefBipo.clicked.connect(self._fcn_refPanelDisp)
        self._ToolsRefApply.clicked.connect(self._fcn_refApply)
        self._fcn_refPanelDisp()

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

    def _fcn_refPanelDisp(self):
        """Display / Hide the reference panel."""
        viz = self._ToolsRefSingle.isChecked()
        self._ToolsRefSingleW.setVisible(viz)
        self._ToolsRefBipoW.setVisible(not viz)

    def _fcn_refApply(self):
        """Apply re-referencing."""
        # ________ Clean ________
        # GUI :
        self._fcn_cleanGui()
        # Visuals :
        self._chan.clean()
        self._hyp.clean()
        self._spec.clean()
        self._specInd.clean()
        self._hypInd.clean()
        self._TimeAxis.clean()
        del (self._chan, self._hyp, self._spec, self._specInd, self._hypInd,
             self._TimeAxis)

        # ________ Re-reference ________
        if self._ToolsRefSingle.isChecked():
            # Get selected channel :
            idx = self._ToolsRefLst.currentIndex()
            chan = self._channels[idx]
            # Build indexing and remove idx :
            index = np.arange(len(self._channels))
            index = np.delete(index, idx)
            # Re-reference :
            self._data -= self._data[[idx], ...]
            # Delete unused row (this operation make a data copy. Because
            # there's might be a gap in indexing, it don't seems possible to
            # take a view of it)
            self._data = self._data[index, :]
            # Channel processing :
            del self._channels[idx]
            self._channels = [k + '-' + chan for k in self._channels]
            # Clean memory :
            gc.collect()

        # ________ Bipolarization ________
        else:
            pass

        # ________ Reset GUI ________
        # Update data info :
        self._get_dataInfo()
        # Reset visuals, shortcuts and GUI elements :
        self._fcn_resetGui()

        # Finally disable GroupBox :
        self._ToolsRefGrp.setEnabled(False)

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
        filttype = str(self._SigFiltMeth.currentText())
        filtorder = self._SigFiltOrder.value()
        filtband = str(self._SigFiltBand.currentText())

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
        filtband = str(self._SigFiltBand.currentText())
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
