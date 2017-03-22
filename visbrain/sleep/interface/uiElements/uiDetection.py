"""Main class for sleep tools managment."""
import numpy as np
import os
from warnings import warn

from ....utils import remdetect, spindlesdetect, slowwavedetect

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
        # Slow Wave detection :
        self._ToolWaveTh.setValue(1.)

        # -------------------------------------------------
        # Spindles detection :
        self._ToolSpinTh.setValue(2.)
        self._ToolSpinFmax.setValue(14.)

        # -------------------------------------------------
        # Location table :
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
        self._ToolDetecReport.setEnabled(viz)
        self._ToolDetectChan.setEnabled(viz)
        self.q_DetectLoc.setEnabled(viz)
        self._DetectionTab.setTabEnabled(1, viz)
        self._hyp.report.visible = viz

    # =====================================================================
    # ENABLE / DISABLE DETECTION
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

    # =====================================================================
    # SWITCH DETECTION TYPE
    # =====================================================================
    def _fcn_switchDetection(self):
        """Switch between detection types (show / hide panels)."""
        # Define ref :
        ref = ['REM', 'Spindles', 'Peaks', 'Slow waves']
        # Get current selected text :
        viz = [str(self._ToolDetectType.currentText()) == k for k in ref]
        # Set widget visibility :
        _ = [k.setVisible(i) for k, i in zip([self._ToolRemPanel,
                                              self._ToolSpinPanel,
                                              self._ToolPeakPanel,
                                              self._ToolWavePanel], viz)]

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
        """Apply detection (either REM / Spindles / Peaks / Slow Wave."""
        # Get channels to apply detection and the detection method :
        idx = self._fcn_getChanDetection()
        method = str(self._ToolDetectType.currentText())
        ind = np.array([], dtype=int)

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
                rem_only = self._ToolRemOnly.isChecked()
                # Get REM indices :
                index, number, density, duration = remdetect(
                    self._data[k, :],
                    self._sf, self._hypno, rem_only, thr)
                if index.size:
                    # Set them + color to ChannelPlot object :
                    self._chan.colidx[k]['color'] = self._defrem
                    self._chan.colidx[k]['idx'] = index
                    # Find only where index start / finish :
                    ind = np.where(np.gradient(index) != 1.)[0]
                    ind = index[np.hstack(([0], ind, [len(index) - 1]))]
                    # Report index on hypnogram :
                    if toReport:
                        # Display on hypnogram :
                        self._hyp.set_report(self._time, ind, y=1.5,
                                             symbol='triangle_down',
                                             color=self._defrem)
                else:
                    warn("\nNo REM detected on channel "+self._channels[k]+"."
                         " Try to decrease the threshold")

            # ------------------- SPINDLES -------------------
            elif method == 'Spindles':
                # Get variables :
                thr = self._ToolSpinTh.value()
                fMin = self._ToolSpinFmin.value()
                fMax = self._ToolSpinFmax.value()
                tMin = self._ToolSpinTmin.value()
                tMax = self._ToolSpinTmax.value()
                nrem_only = self._ToolSpinRemOnly.isChecked()
                # Get Spindles indices :
                index, number, density, duration = spindlesdetect(
                    self._data[k, :],
                    self._sf, thr,
                    self._hypno, nrem_only,
                    fMin, fMax, tMin, tMax)
                if index.size:
                    # Set them + color to ChannelPlot object :
                    self._chan.colidx[k]['color'] = self._defspin
                    self._chan.colidx[k]['idx'] = index
                    # Find only where index start / finish :
                    ind = np.where(np.gradient(index) != 1.)[0]
                    ind = index[np.hstack(([0], ind, [len(index) - 1]))]
                    # Report index on hypnogram :
                    if toReport:
                        # Display on hypnogram :
                        self._hyp.set_report(self._time, ind, symbol='x',
                                             color=self._defspin, y=1.5)

                    # Report results on table
                    self._ToolSpinTable.setRowCount(1)
                    self._ToolSpinTable.setItem(0, 0, QtGui.QTableWidgetItem(
                        str(number)))
                    self._ToolSpinTable.setItem(0, 1, QtGui.QTableWidgetItem(
                        str(round(density, 2))))
                else:
                    warn("\nNo Spindles detected on channel "+self._channels[
                         k]+". Try to decrease the threshold")

            # ------------------- SLOW WAVES -------------------
            elif method == 'Slow waves':
                # Get variables :
                thr = self._ToolWaveTh.value()
                amp = self._ToolWaveAmp.value()
                # Get Slow Waves indices :
                index, number, duration = slowwavedetect(self._data[k, :],
                                                         self._sf, thr, amp)

                if index.size:
                    # Set them + color to ChannelPlot object :
                    self._chan.colidx[k]['color'] = self._defslowwave
                    self._chan.colidx[k]['idx'] = index
                    # Find only where index start / finish :
                    ind = np.where(np.gradient(index) != 1.)[0]
                    ind = index[np.hstack(([0], ind, [len(index) - 1]))]
                    # Report index on hypnogram :
                    if toReport:
                        # Display on hypnogram :
                        self._hyp.set_report(self._time, ind, symbol='o',
                                             color=self._defslowwave, y=1.5)

                else:
                    warn("\nNo Slow Wave detected on channel "+self._channels[
                         k]+". Try to decrease the threshold")

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
                # Get index :
                ind = self._peak.index
                duration = 0
                # Report index on hypnogram :
                if toReport:
                    self._hyp.set_report(self._time, self._peak.index,
                                         color=self._defpeaks, symbol='vbar',
                                         y=1.5)

            # Be sure panel is displayed :
            if not self.canvas_isVisible(k):
                self.canvas_setVisible(k, True)
                self._chan.visible[k] = True

            # Update plot :
            self._fcn_sliderMove()

            # Update progress bar :
            self._ToolDetectProgress.setValue(100. * (i + 1) / len(self))

        # Fill the location table (only if selected):
        if self._ToolRdSelected.isChecked() and ind.size:
            self._fcn_fillLocations(self._channels[k], method, ind, duration)

        # Finally, hide progress bar :
        self._ToolDetectProgress.hide()

    # =====================================================================
    # FILL LOCATION TABLE
    # =====================================================================
    def _fcn_fillLocations(self, channel, kind, index, duration):
        """Fill the location table."""
        ref = ['Wake', 'N1', 'N2', 'N3', 'REM', 'ART']
        # Set header label :
        self._DetectLocHead.setText(kind + ' detection on channel ' + channel)
        # Clean table :
        self._DetectLocations.setRowCount(0)
        # Get kind :
        kindIn = kind in ['REM', 'Spindles', 'Slow waves']
        if kindIn and self._ToolRdSelected.isChecked():
            # Define the length of the table:
            self._DetectLocations.setRowCount(int(len(index) / 2))
            # Get starting index:
            staInd = index[0::2]
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
                    ''))
                # Type :
                self._DetectLocations.setItem(num, 2, QtGui.QTableWidgetItem(
                    ref[int(self._hypno[k])]))

    def _fcn_gotoLocation(self):
        """Go to the selected row REM / spindles / peak."""
        # Get selected row :
        row = self._DetectLocations.currentRow()
        # Get starting and ending point :
        st = float(str(self._DetectLocations.item(row, 0).text()))
        # Go to :
        self._SlGoto.setValue(
            st - self._SigWin.value() / self._SigSlStep.value())
            
    def _fcn_exportLocation(self):
        """Export locations info."""
        method = str(self._ToolDetectType.currentText())   
        # Read Table
        rowCount = self._DetectLocations.rowCount()
        staInd = np.zeros(shape=(rowCount,))
        duration = np.zeros(shape=(rowCount,))
        stage = np.zeros(shape=(rowCount,), dtype=str)
        for row in np.arange(0, rowCount):
            staInd[row] = str(self._DetectLocations.item(row, 0).text())
            duration[row] = str(self._DetectLocations.item(row, 1).text())
            stage[row] = str(self._DetectLocations.item(row, 2).text())
        # Find extension :
        selected_ext = str(self._DetectLocExportAs.currentText())
        # Get file name :
        path = QtGui.QFileDialog.getSaveFileName(
            self, "Save File", method + "_locinfo",
            filter=selected_ext)
        file = os.path.splitext(str(path))[0]
        if selected_ext.find('csv') + 1:
            self.listToCsv(file + '.csv', zip(staInd, duration, stage))
        elif selected_ext.find('txt') + 1:
            self.listToTxt(file + '.txt', zip(staInd.astype(str), duration.astype(str), stage))

    def listToCsv(self, file, data):
        """Write a csv file.

        Args:
            file: string
                File name for saving file.

            data: list
                List of data to save to the csv file.
        """
        with open(file, 'w') as csvfile:
            writer = csv.writer(csvfile, dialect='excel',
                                quoting=csv.QUOTE_NONNUMERIC)
            for k in data:
                writer.writerow(k)
        return

    def listToTxt(self, file, data):
        """Write a txt file.

        Args:
            file: string
                File name for saving file.

            data: list
                List of data to save to the txt file.
        """
        # Open file :
        ofile = open(file, 'w')
        for k in data:
            ofile.write("%s\n" % ', '.join(k))
        return
