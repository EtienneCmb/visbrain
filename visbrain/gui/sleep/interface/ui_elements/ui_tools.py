"""Main class for sleep tools managment."""

import numpy as np
from PyQt5 import QtWidgets
from visbrain.utils import (rereferencing, bipolarization, find_non_eeg,
                            commonaverage)


class UiTools(object):
    """Main class for sleep tools managment."""

    def __init__(self):
        """Init."""
        self._tool_pick.currentIndexChanged.connect(self._fcn_tool_pick)
        # Find non-eeg channels :
        self._noneeg = find_non_eeg(self._channels)
        # =====================================================================
        # RE-REFERENCING
        # =====================================================================
        # Add channels to scrolling area :
        self._ToolsRefIgnArea.setVisible(False)
        self._reChecks = []
        for i, k in enumerate(self._channels):
            if not self._noneeg[i]:
                # Add a checkbox to the scrolling panel :
                box = QtWidgets.QCheckBox(self._PanScrollChan)
                # Name checkbox with channel name :
                box.setText(k)
                # Get it :
                self._reChecks.append(box)
                # Add checkbox to the grid :
                self._ToolsRefIgnGrd.addWidget(box, i, 0, 1, 1)
        # Connections :
        self._ToolsRefIgn.clicked.connect(self._fcn_ref_chan_ignore)
        self._ToolsRefLst.addItems(np.array(self._channels)[~self._noneeg])
        self._ToolsRefMeth.currentIndexChanged.connect(self._fcn_ref_switch)
        self._ToolsRefApply.clicked.connect(self._fcn_ref_apply)
        self._fcn_ref_switch()

        # =====================================================================
        # MEAN / TREND
        # =====================================================================
        self._SigMean.clicked.connect(self._fcn_sig_processing)
        self._SigTrend.clicked.connect(self._fcn_sig_processing)

        # =====================================================================
        # FILTERING
        # =====================================================================
        self._SigFiltChan.addItems(self._channels)
        self._SigFiltDisp.currentIndexChanged.connect(self._fcn_filt_disp_as)
        self._SigFiltApply.clicked.connect(self._fcn_sig_processing)
        self._SigFilt.clicked.connect(self._fcn_filt_viz)
        self._SigFiltBand.currentIndexChanged.connect(self._fcn_filt_band)

    def _fcn_tool_pick(self):
        """Change tool type."""
        idx = int(self._tool_pick.currentIndex())
        self._stacked_tools.setCurrentIndex(idx)

    # =====================================================================
    # RE-REFERENCING
    # =====================================================================
    def _fcn_ref_switch(self):
        """Switch between re-referencing methods."""
        idx = int(self._ToolsRefMeth.currentIndex())
        # Single channel :
        if idx == 0:  # Single channel
            self._ToolsRefSingleW.setVisible(True)
        elif idx == 1:  # Common average
            self._ToolsRefSingleW.setVisible(False)
        elif idx == 2:  # Bipolarization
            self._ToolsRefSingleW.setVisible(False)

    def _fcn_ref_chan_ignore(self):
        """Display / hide list of channels to ignore."""
        self._ToolsRefIgnArea.setVisible(self._ToolsRefIgn.isChecked())

    def _fcn_ref_apply(self):
        """Apply re-referencing."""
        # By default, ingore non-eeg channel :
        to_ignore = self._noneeg
        if self._ToolsRefIgn.isChecked():
            for num, k in enumerate(self._reChecks):
                # Get the position of this channel :
                idinlst = self._channels.index(str(k.text()))
                # Set to ignore :
                to_ignore[idinlst] = k.isChecked()

        # Get the current selected method :
        idx = int(self._ToolsRefMeth.currentIndex())
        # Single channel :
        if idx == 0:  # Single channel
            # Get selected channel :
            idchan = idx = self._ToolsRefLst.currentIndex()
            # Re-referencing :
            self._data, self._channels, consider = rereferencing(
                self._data, self._channels, idchan,
                to_ignore)
            self._chanChecks[idx].setChecked(False)
        elif idx == 1:  # Common average
            self._data, self._channels, consider = commonaverage(
                self._data, self._channels, to_ignore)
        elif idx == 2:  # Bipolarization
            self._data, self._channels, consider = bipolarization(
                self._data, self._channels,
                to_ignore)

        # ____________________ Update ____________________
        a_max = np.argmax(consider)
        # Update data info :
        self._get_data_info()

        # Update and clear detections :
        self._DetectLocations.setRowCount(0)
        self._DetectChanSw.clear()
        self._detect.update_keys(self._channels)
        self._detect.reset()

        # Disconnect and clear listbox :
        self._PanSpecChan.currentIndexChanged.disconnect()
        self._PanSpecChan.clear()
        self._ToolDetectChan.clear()
        self._PanSpecChan.addItems(self._channels)
        self._ToolDetectChan.addItems(self._channels)
        # Reconnect :
        self._PanSpecChan.setCurrentIndex(a_max)
        self._ToolDetectChan.setCurrentIndex(a_max)

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
            self._chanChecks[a_max].setChecked(True)
        # Reconnect :
        self._PanSpecChan.currentIndexChanged.connect(self._fcn_spec_set_data)

        self._chan.update()
        self._fcn_chan_viz()

        # Finally disable GroupBox :
        self._ToolsRefGrp.setEnabled(False)

    # =====================================================================
    # DEMEAN / DETREND / FILTERING
    # =====================================================================
    def _fcn_sig_processing(self):
        """Signal processing function."""
        # ========== VALUES ==========
        # Mean and trend :
        demean = self._SigMean.isChecked()
        detrend = self._SigTrend.isChecked()
        # Filtering :
        dispas = self._SigFiltDisp.currentText()
        filt = self._SigFilt.isChecked()
        fstart = self._SigFiltFrom.value()
        fend = self._SigFiltTo.value()
        filttype = str(self._SigFiltMeth.currentText())
        filtorder = self._SigFiltOrder.value()
        filtband = str(self._SigFiltBand.currentText())

        # Filt a specific channel :
        channel = int(self._SigFiltChan.currentIndex()) - 1
        if channel >= 0:
            self._chanChecks[channel].setChecked(True)
            self._fcn_chan_viz()

        # ========== CHANNELS ==========
        # ---- Demean / detrend ----
        self._chan._preproc_channel = channel
        self._chan.demean = demean
        self._chan.detrend = detrend
        # ---- Filtering ----
        self._chan.dispas = dispas
        self._chan.filt = filt
        self._chan.fstart = fstart
        self._chan.fend = fend
        self._chan.forder = filtorder
        self._chan.filt_type = filttype
        self._chan.filt_band = filtband

        self._chan.update()

        # ========== SPECTROGRAM ==========
        chan = self._PanSpecChan.currentIndex()
        # ---- Demean / detrend ----
        self._spec.demean = demean
        self._spec.detrend = detrend
        # ---- Filtering ----
        self._spec.dispas = dispas
        self._spec.filt = filt and channel in [-1, chan]
        self._spec.fstart = fstart
        self._spec.fend = fend
        self._spec.forder = filtorder
        self._spec.filt_type = filttype
        self._spec.filt_band = filtband

        self._spec.update()

    def _fcn_filt_disp_as(self):
        """Display / hide settings for amplitude / phase / power."""
        # Get current type :
        dispas = self._SigFiltDisp.currentText()
        if dispas == 'filter':
            self._SigFiltBand.setEnabled(True)
            self._SigFiltMeth.setEnabled(True)
            self._SigFiltOrder.setEnabled(True)
            self._fcn_filt_band()
        else:
            self._SigFiltBand.setEnabled(False)
            self._SigFiltMeth.setEnabled(False)
            self._SigFiltOrder.setEnabled(False)
        # Run filter :
        self._fcn_sig_processing()

    def _fcn_filt_viz(self):
        """Display / hide filtering panel."""
        viz = self._SigFilt.isChecked()
        self._SigFiltW.setEnabled(viz)
        if not viz:
            self._fcn_sig_processing()

    def _fcn_filt_band(self):
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
