"""Main class for sleep tools managment."""
import numpy as np

from ....utils import remdetect, spindlesdetect

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
        # Spindles detection :
        self._ToolSpinTh.setValue(2.)
        self._ToolSpinFmax.setValue(14.)

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
        ref = ['REM', 'Spindles', 'Peaks']
        # Get current selected text :
        viz = [self._ToolDetectType.currentText() == k for k in ref]
        # Set widget visibility :
        _ = [k.setVisible(i) for k, i in zip([self._ToolRemPanel,
                                              self._ToolSpinPanel,
                                              self._ToolPeakPanel], viz)]

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
                rem_only = self._ToolRemOnly.isChecked()
                # Get REM indices :
                index, _, _ = remdetect(self._data[k, :], self._sf,
                                        self._hypno, rem_only, thr)
                # Set them to ChannelPlot object :
                self._chan.colidx[k] = index
                # Report index on hypnogram :
                if toReport:
                    # Find only where index start :
                    ind = index[np.where(index[1:]-index[:-1] != 1)[0]]
                    # Display on hypnogram :
                    self._hyp.set_report(self._time, ind, color='slateblue',
                                         symbol='triangle_down',
                                         y=-self._hypno[ind] + .2)

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
                index, number, density = spindlesdetect(self._data[k, :],
                                                        self._sf, thr,
                                                        self._hypno, nrem_only,
                                                        fMin, fMax, tMin, tMax)
                # Set them to ChannelPlot object :
                self._chan.colidx[k] = index
                # Report index on hypnogram :
                if toReport:
                    # Find only where index start :
                    ind = index[np.where(index[1:]-index[:-1] != 1)[0]]
                    # Display on hypnogram :
                    self._hyp.set_report(self._time, ind, color='olive',
                                         symbol='x', y=-self._hypno[ind] + .2)

                # Report results on table
                self._ToolSpinTable.setRowCount(1)
                self._ToolSpinTable.setItem(0, 0, QtGui.QTableWidgetItem(
                    str(number)))
                self._ToolSpinTable.setItem(0, 1, QtGui.QTableWidgetItem(
                    str(round(density, 2))))

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
                                         y=-self._hypno[self._peak.index] + .2)
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
