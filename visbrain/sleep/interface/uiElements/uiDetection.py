"""Main class for sleep tools managment."""
import numpy as np
import os
from warnings import warn

from ....utils import (remdetect, spindlesdetect, slowwavedetect, kcdetect,
                       peakdetect, listToCsv, listToTxt)
from ....utils.sleep.event import _events_duration

from PyQt4 import QtGui

__all__ = ['uiDetection']


class uiDetection(object):
    """Main class for sleep tools managment."""

    def __init__(self):
        """Init."""
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
        # Location table :
        self._DetectChans.currentIndexChanged.connect(self._fcn_switchLocation)
        self._DetectTypes.currentIndexChanged.connect(self.__getVisibleLoc)
        self._DetectSelect.clicked.connect(self._fcn_runSwitchLocation)
        self._DetectRm.clicked.connect(self._fcn_rmLocation)
        self._DetectViz.clicked.connect(self._fcn_vizLocation)
        self._DetectLocations.itemSelectionChanged.connect(
            self._fcn_gotoLocation)

        # Export file :
        self._DetectLocExport.clicked.connect(self._fcn_exportLocation)

    # =====================================================================
    # ENABLE / DISABLE GUI COMPONENTS (based on selected channels)
    # =====================================================================
    def _fcn_applyMethod(self):
        """Be sure to apply hypnogram report only on selected channel."""
        viz = self._ToolRdSelected.isChecked()
        self._ToolDetectChan.setEnabled(viz)

    # =====================================================================
    # SWITCH DETECTION TYPE
    # =====================================================================
    def _fcn_switchDetection(self):
        """Switch between detection types (show / hide panels)."""
        # Define ref :
        ref = ['REM', 'Spindles', 'Peaks', 'Slow waves', 'K-complexes']
        # Get current selected text :
        viz = [str(self._ToolDetectType.currentText()) == k for k in ref]
        # Set widget visibility :
        _ = [k.setVisible(i) for k, i in zip([self._ToolRemPanel,
                                              self._ToolSpinPanel,
                                              self._ToolPeakPanel,
                                              self._ToolWavePanel,
                                              self._ToolKCPanel], viz)]

    # =====================================================================
    # RUN DETECTION
    # =====================================================================
    # -------------- Get channels to apply detection --------------
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

    # -------------- Run detection (only on selected channels) --------------
    def _fcn_applyDetection(self):
        """Apply detection (either REM / Spindles / Peaks / Slow Wave / KC)."""
        # Get channels to apply detection and the detection method :
        idx = self._fcn_getChanDetection()
        method = str(self._ToolDetectType.currentText())

        ############################################################
        # RUN DETECTION
        ############################################################
        for i, k in enumerate(idx):
            # Display progress bar (only if needed):
            if len(idx) > 1:
                self._ToolDetectProgress.show()

            # Switch between detection types :
            # ====================== REM ======================
            if method == 'REM':
                # Get variables :
                thr = self._ToolRemTh.value()
                rem_only = self._ToolRemOnly.isChecked()
                # Get REM indices :
                index, nb, dty, dur = remdetect(self._data[k, :], self._sf,
                                                self._hypno, rem_only, thr)
                # Update index for this channel and detection :
                self._detect.dict[(self._channels[k], 'REM')]['index'] = index

            # ====================== SPINDLES ======================
            elif method == 'Spindles':
                # Get variables :
                thr = self._ToolSpinTh.value()
                fMin = self._ToolSpinFmin.value()
                fMax = self._ToolSpinFmax.value()
                tMin = self._ToolSpinTmin.value()
                tMax = self._ToolSpinTmax.value()
                nrem_only = self._ToolSpinRemOnly.isChecked()
                # Get Spindles indices :
                index, nb, dty, dur = spindlesdetect(
                    self._data[k, :], self._sf, thr, self._hypno, nrem_only,
                    fMin, fMax, tMin, tMax)
                # Update index for this channel and detection :
                self._detect.dict[(self._channels[k], 'Spindles')][
                                                            'index'] = index

            # ====================== SLOW WAVES ======================
            elif method == 'Slow waves':
                # Get variables :
                thr = self._ToolWaveTh.value()
                amp = self._ToolWaveAmp.value()
                # Get Slow Waves indices :
                index, nb, dty, dur = slowwavedetect(self._data[k, :],
                                                     self._sf, thr, amp)
                # Update index for this channel and detection :
                self._detect.dict[(self._channels[k], 'Slow waves')][
                                                            'index'] = index

            # ====================== K-COMPLEXES ======================
            elif method == 'K-complexes':
                # Get variables :
                proba_thr = self._ToolKCProbTh.value()
                amp_thr = self._ToolKCAmpTh.value()
                tmin = self._ToolKCMinDur.value()
                tmax = self._ToolKCMaxDur.value()
                min_amp = self._ToolKCMinAmp.value()
                max_amp = self._ToolKCMaxAmp.value()
                nrem_only = self._ToolKCNremOnly.isChecked()
                # Get Slow Waves indices :
                index, nb, dty, dur = kcdetect(self._data[k, :], self._sf,
                                               proba_thr, amp_thr, self._hypno,
                                               nrem_only, tmin, tmax, min_amp,
                                               max_amp)
                # Update index for this channel and detection :
                self._detect.dict[(self._channels[k], 'K-complexes')][
                                                            'index'] = index

            # ====================== PEAKS ======================
            elif method == 'Peaks':
                # Get variables :
                look = int(self._ToolPeakLook.value() * self._sf)
                disp = self._ToolPeakMinMax.currentIndex()
                disp_types = ['max', 'min', 'minmax']
                index, nb, dty = peakdetect(self._sf, self._data[k, :],
                                            self._time, lookahead=look,
                                            delta=1., threshold='auto',
                                            get=disp_types[disp])
                self._detect.dict[(self._channels[k], 'Peaks')][
                                                            'index'] = index

            if index.size:
                # Be sure panel is displayed :
                if not self.canvas_isVisible(k):
                    self.canvas_setVisible(k, True)
                    self._chan.visible[k] = True
                # Update plot :
                self._fcn_sliderMove()

            # Update progress bar :
            self._ToolDetectProgress.setValue(100. * (i + 1) / len(self))

        ############################################################
        # NUMBER // DENSITY
        ############################################################
        if index.size:
            # Report results on table :
            self._ToolDetectTable.setRowCount(1)
            self._ToolDetectTable.setItem(0, 0, QtGui.QTableWidgetItem(
                str(nb)))
            self._ToolDetectTable.setItem(0, 1, QtGui.QTableWidgetItem(
                str(round(dty, 2))))
        else:
            warn("\nNo " + method + " detected on channel " + self._channels[
                 k] + ". Try to decrease the threshold")

        ############################################################
        # LINE REPORT :
        ############################################################
        # Build line reports :
        self._detect.build_line(self._data)
        chans = self._detect.nonzero()
        self._DetectChans.clear()
        self._DetectChans.addItems(list(chans.keys()))
        self._fcn_runSwitchLocation()

        # Finally, hide progress bar :
        self._ToolDetectProgress.hide()

    # =====================================================================
    # FILL LOCATION TABLE
    # =====================================================================
    def _fcn_switchLocation(self):
        """Switch location channel and type."""
        # Get selected channel :
        chan = str(self._DetectChans.currentText())
        nnz = self._detect.nonzero()
        # Update list of types :
        self._DetectTypes.clear()
        if chan:
            # Set avaibles detection types :
            self._DetectTypes.addItems(nnz[chan])
            # Set visibility :
            self.__getVisibleLoc()

    def __getVisibleLoc(self):
        chan = str(self._DetectChans.currentText())
        tps = str(self._DetectTypes.currentText())
        if chan and tps:
            if tps == 'Peaks':
                self._DetectViz.setChecked(self._detect.peaks[(chan,
                                                              tps)].visible)
            else:
                self._DetectViz.setChecked(self._detect.line[(chan,
                                                              tps)].visible)

    def _fcn_rmLocation(self):
        """Demove a detection."""
        # Get selected channel :
        chan = str(self._DetectChans.currentText())
        # Get selected detection type :
        types = str(self._DetectTypes.currentText())
        # Remove detection :
        self._detect[(chan, types)]['index'] = np.array([])
        # Update GUI :
        self._fcn_switchLocation()

    def _fcn_vizLocation(self):
        """Set visible detection."""
        # Get selected channel :
        chan = str(self._DetectChans.currentText())
        # Get selected detection type :
        types = str(self._DetectTypes.currentText())
        # Set visibility :
        self._detect.visible(self._DetectViz.isChecked(), chan, types)

    def _fcn_runSwitchLocation(self):
        """Run switch location channel and type."""
        # Get selected channel :
        chan = str(self._DetectChans.currentText())
        # Get selected detection type :
        types = str(self._DetectTypes.currentText())
        if chan and types:
            # Find index and durations :
            index = self._detect[(chan, types)]['index']
            # Get durations :
            _, dur, _, _ = _events_duration(index, self._sf)
            # Find only where index start / finish :
            ind = np.where(np.gradient(index) != 1.)[0]
            ind = index[np.hstack(([0], ind, [len(index) - 1]))]
            # Set hypnogram data :
            self._detect.build_hyp(chan, types)
            # Fill location table :
            self._fcn_fillLocations(chan, types, ind, dur)

    def _fcn_fillLocations(self, channel, kind, index, duration):
        """Fill the location table."""
        ref = ['Wake', 'N1', 'N2', 'N3', 'REM', 'ART']
        # Clean table :
        self._DetectLocations.setRowCount(0)
        # Get kind :
        kindIn = kind in ['REM', 'Spindles', 'Slow waves', 'K-complexes']
        if kindIn:
            # Get starting index:
            staInd = index[0::2]
            # Define the length of the table:
            self._DetectLocations.setRowCount(min(len(staInd), len(duration)))
            # Fill the table :
            for num, (k, i) in enumerate(zip(staInd, duration)):
                # Starting :
                self._DetectLocations.setItem(num, 0, QtGui.QTableWidgetItem(
                    str(self._time[k])))
                # Duration :
                self._DetectLocations.setItem(num, 1, QtGui.QTableWidgetItem(
                    str(i)))
                # Type :
                self._DetectLocations.setItem(num, 2, QtGui.QTableWidgetItem(
                    ref[int(self._hypno[k])]))

        elif kind == 'Peaks':
            # Define the length of the table :
            self._DetectLocations.setRowCount(len(index))
            # Fill the table :
            for num, k in enumerate(index):
                # Starting :
                self._DetectLocations.setItem(num, 0, QtGui.QTableWidgetItem(
                    str(self._time[k])))
                # Duration :
                self._DetectLocations.setItem(num, 1, QtGui.QTableWidgetItem(
                    '1'))
                # Type :
                self._DetectLocations.setItem(num, 2, QtGui.QTableWidgetItem(
                    ref[int(self._hypno[k])]))

        self._DetectLocations.selectRow(0)

    # =====================================================================
    # GO TO THE LOCATION
    # =====================================================================
    def _fcn_gotoLocation(self):
        """Go to the selected row REM / spindles / peak."""
        # Get selected row and channel :
        row = self._DetectLocations.currentRow()
        ix = self._channels.index(str(self._DetectChans.currentText()))
        if row >= 0:
            # Get starting and ending point :
            sta = float(str(self._DetectLocations.item(row, 0).text()))
            end = sta + float(str(self._DetectLocations.item(row, 1).text())) \
                / 1000.
            # Get best looking location :
            goto = ((sta + end) / 2.) - (self._SigWin.value() / 2.)
            # Go to :
            self._SigSlStep.setValue(1)
            self._SlGoto.setValue(goto)
            # Set vertical lines to the location :
            self._chan.set_location(self._sf, self._data[ix, :], ix, sta, end)

    # =====================================================================
    # EXPORT TABLE
    # =====================================================================
    def _fcn_exportLocation(self):
        """Export locations info."""
        method = str(self._ToolDetectType.currentText())
        # Read Table
        rowCount = self._DetectLocations.rowCount()
        staInd, duration, stage = [], [], []
        for row in np.arange(rowCount):
            staInd.append(str(self._DetectLocations.item(row, 0).text()))
            duration.append(str(self._DetectLocations.item(row, 1).text()))
            stage.append(str(self._DetectLocations.item(row, 2).text()))
        # Find extension :
        selected_ext = str(self._DetectLocExportAs.currentText())
        # Get file name :
        path = QtGui.QFileDialog.getSaveFileName(
            self, "Save File", method + "_locinfo",
            filter=selected_ext)
        path = str(path)  # py2
        if path:
            file = os.path.splitext(str(path))[0]
            if selected_ext.find('csv') + 1:
                listToCsv(file + '.csv', zip(staInd, duration, stage))
            elif selected_ext.find('txt') + 1:
                listToTxt(file + '.txt', zip(staInd, duration, stage))
