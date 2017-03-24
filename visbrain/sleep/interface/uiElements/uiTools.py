"""Main class for sleep tools managment."""

import numpy as np
from PyQt4 import QtGui
from ....utils import rereferencing, bipolarization, id

__all__ = ['uiTools']


class uiTools(object):
    """Main class for sleep tools managment."""

    def __init__(self):
        """Init."""
        # =====================================================================
        # RE-REFERENCING
        # =====================================================================
        # Add channels to scrolling area :
        self._ToolsRefIgnArea.setVisible(False)
        self._reChecks = [0] * len(self._channels)
        for i, k in enumerate(self._channels):
            # Add a checkbox to the scrolling panel :
            self._reChecks[i] = QtGui.QCheckBox(self._PanScrollChan)
            # Name checkbox with channel name :
            self._reChecks[i].setText(k)
            # Add checkbox to the grid :
            self._ToolsRefIgnGrd.addWidget(self._reChecks[i], i, 0, 1, 1)
        # Connections :
        self._ToolsRefIgn.clicked.connect(self._fcn_refChanIgnore)
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

    # =====================================================================
    # RE-REFERENCING
    # =====================================================================
    def _fcn_refChanIgnore(self):
        """Display / hide list of channels to ignore."""
        self._ToolsRefIgnArea.setVisible(self._ToolsRefIgn.isChecked())

    def _fcn_refPanelDisp(self):
        """Display / Hide the reference panel."""
        viz = self._ToolsRefSingle.isChecked()
        self._ToolsRefSingleW.setVisible(viz)
        # self._ToolsRefBipoW.setVisible(not viz)

    def _fcn_refApply(self):
        """Apply re-referencing."""
        # Get selected channel :
        idx = self._ToolsRefLst.currentIndex()
        if self._ToolsRefIgn.isChecked():
            to_ignore = [num for num, k in enumerate(
                                             self._reChecks) if k.isChecked()]
        else:
            to_ignore = None

        # ____________________ Re-reference ____________________
        if self._ToolsRefSingle.isChecked():
            self._data, self._channels, consider = rereferencing(
                                            self._data, self._channels, idx,
                                            to_ignore)
            self._chanChecks[idx].setChecked(False)

        # ____________________ Bipolarization ____________________
        else:
            self._data, self._channels, consider = bipolarization(
                                                  self._data, self._channels,
                                                  to_ignore)

        # ____________________ Update ____________________
        aM = np.argmax(consider)
        # Update data info :
        self._get_dataInfo()

        # Disconnect and clear listbox :
        self._PanSpecChan.currentIndexChanged.disconnect()
        self._PanSpecChan.clear()
        self._ToolDetectChan.clear()
        self._PanSpecChan.addItems(self._channels)
        self._ToolDetectChan.addItems(self._channels)
        # Reconnect :
        self._PanSpecChan.setCurrentIndex(aM)
        self._ToolDetectChan.setCurrentIndex(aM)
        self._ToolDetectChan.model().item(idx).setEnabled(False)

        # Update channel names :
        for num, k in enumerate(self._channels):
            self._chanChecks[num].setText(k)
            self._chanLabels[num].setText(k)

        # Ignore non re-referenced channels :
        if self._ToolsRefIgnore.isChecked():
            for num, k in enumerate(consider):
                # Remove from visible channels :
                self._chanChecks[num].setChecked(False)
                self._chanChecks[num].setVisible(k)
                self._chanLabels[num].setVisible(k)
                self._yminSpin[num].setVisible(k)
                self._ymaxSpin[num].setVisible(k)
                self._amplitudeTxt[num].setVisible(k)
                # Remove from chan list :
                self._PanSpecChan.model().item(num).setEnabled(k)
                self._ToolDetectChan.model().item(num).setEnabled(k)
        if not any([k.isChecked() for k in self._chanChecks]):
            self._chanChecks[aM].setChecked(True)
        # Reconnect :
        self._PanSpecChan.currentIndexChanged.connect(self._fcn_specSetData)

        self._chan.update()
        self._fcn_chanViz()

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
