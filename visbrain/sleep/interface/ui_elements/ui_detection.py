"""Main class for sleep tools managment."""
import numpy as np
from warnings import warn
from PyQt5 import QtWidgets, QtCore
import logging

from ....utils import (remdetect, spindlesdetect, slowwavedetect, kcdetect,
                       peakdetect, mtdetect)
from ....utils.sleep.event import _events_to_index

logger = logging.getLogger('visbrain')


class UiDetection(object):
    """Main class for sleep tools managment."""

    def __init__(self):
        """Init."""
        # =====================================================================
        # REM / SPINDLES / KC / SW / MT DETECTION
        # =====================================================================
        # Commonth elements :
        self._ToolDetectChan.addItems(self._channels)
        self._ToolDetectType.currentIndexChanged.connect(
            self._fcn_switch_detection)
        self._ToolDetectApply.clicked.connect(self._fcn_apply_detection)
        # Apply method (Selected / Visible / All) :
        self._ToolRdSelected.clicked.connect(self._fcn_apply_method)
        self._ToolRdViz.clicked.connect(self._fcn_apply_method)
        self._ToolRdAll.clicked.connect(self._fcn_apply_method)
        self._ToolDetectProgress.hide()
        self._fcn_switch_detection()

        # -------------------------------------------------
        # Location table :
        self._DetectChanSw.currentIndexChanged.connect(
            self._fcn_run_switch_location)
        self._DetectRm.clicked.connect(self._fcn_rm_location)
        self._DetectViz.clicked.connect(self._fcn_viz_location)
        self._DetecRmEvent.clicked.connect(self._fcn_rm_selected_event)
        self._DetectLocations.itemSelectionChanged.connect(
            self._fcn_goto_location)
        self._DetectLocations.cellChanged.connect(self._fcn_edit_detection)
        self._DetectionTab.setTabEnabled(1, False)

    # =====================================================================
    # ENABLE / DISABLE GUI COMPONENTS (based on selected channels)
    # =====================================================================
    def _fcn_apply_method(self):
        """Be sure to apply hypnogram report only on selected channel."""
        viz = self._ToolRdSelected.isChecked()
        self._ToolDetectChan.setEnabled(viz)

    # =====================================================================
    # SWITCH DETECTION TYPE
    # =====================================================================
    def _fcn_switch_detection(self):
        """Switch between detection types (show / hide panels)."""
        idx = int(self._ToolDetectType.currentIndex())
        self._stacked_detections.setCurrentIndex(idx)

    # =====================================================================
    # RUN DETECTION
    # =====================================================================
    # -------------- Get channels to apply detection --------------
    def _fcn_get_chan_detection(self):
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
    def _fcn_apply_detection(self):
        """Apply detection (either REM/Spindles/Peaks/SlowWave/KC/MT)."""
        # Get channels to apply detection and the detection method :
        idx = self._fcn_get_chan_detection()
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

            # ====================== SPINDLES ======================
            elif method == 'Spindles':
                # Get variables :
                thr = self._ToolSpinTh.value()
                f_min = self._ToolSpinFmin.value()
                f_max = self._ToolSpinFmax.value()
                t_min = self._ToolSpinTmin.value()
                t_max = self._ToolSpinTmax.value()
                nrem_only = self._ToolSpinRemOnly.isChecked()
                # Get Spindles indices :
                index, nb, dty, dur, pwr = spindlesdetect(
                    self._data[k, :], self._sf, thr, self._hypno, nrem_only,
                    f_min, f_max, t_min, t_max)

            # ====================== SLOW WAVES ======================
            elif method == 'Slow waves':
                # Get variables :
                thr = self._ToolWaveTh.value()
                # Get Slow Waves indices :
                index, nb, dty, dur = slowwavedetect(self._data[k, :],
                                                     self._sf, thr)

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

            # ====================== MUSCLE TWITCHES ======================
            elif method == 'Muscle twitches':
                # Get variables :
                th = self._ToolMTTh.value()
                rem_only = self._ToolMTOnly.isChecked()
                index, nb, dty, dur = mtdetect(self._data[k, :], self._sf, th,
                                               self._hypno, rem_only)

            logger.info(("Perform %s detection on channel %s. %i events "
                         "detected.") % (method, self._channels[k], nb))

            if index.size:
                # Enable detection tab :
                self._DetectionTab.setTabEnabled(1, True)
                # Update index for this channel and detection :
                if method == 'Peaks':
                    index = np.c_[index, index]
                else:
                    index = _events_to_index(index)
                self._detect.dict[(self._channels[k], method)]['index'] = index
                # Be sure panel is displayed :
                if not self._canvas_is_visible(k):
                    self._canvas_set_visible(k, True)
                    self._chan.visible[k] = True
                self._chan.loc[k].visible = True
                # Update plot :
                self._fcn_slider_move()

            # Update progress bar :
            self._ToolDetectProgress.setValue(100. * (i + 1) / len(self))

        ############################################################
        # NUMBER // DENSITY
        ############################################################
        if index.size:
            # Report results on table :
            self._ToolDetectTable.setRowCount(1)
            self._ToolDetectTable.setItem(0, 0, QtWidgets.QTableWidgetItem(
                str(nb)))
            self._ToolDetectTable.setItem(0, 1, QtWidgets.QTableWidgetItem(
                str(round(dty, 2))))
        else:
            warn("\nNo " + method + " detected on channel " + self._channels[
                 k] + ". Try to decrease the threshold")

        ############################################################
        # LINE REPORT :
        ############################################################
        self._loc_line_report()

        # Activate the save detections menu and activate detection tab :
        self._check_detect_menu()

        # Finally, hide progress bar :
        self._ToolDetectProgress.hide()

    def _loc_line_report(self, *args, refresh=True):
        """Update line report."""
        self._detect.build_line(self._data)
        chans = self._detect.nonzero()
        if refresh:
            # Disconnect the table :
            self._DetectChanSw.disconnect()
            # Clear already existing events :
            self._DetectChanSw.clear()
            # Add list of detected event as (chan - type) :
            lst = []
            for k in chans.keys():
                for i in chans[k]:
                    lst.append(k + ' - ' + i)
            self._DetectChanSw.addItems(lst)
        self._fcn_run_switch_location()
        # Disable menu and detection tab if there is no detection :
        if self._DetectChanSw.count() == 0:
            self._DetectionTab.setTabEnabled(1, False)
        else:
            self._DetectionTab.setTabEnabled(1, True)
        self._check_detect_menu()
        # Reconnect table :
        self._DetectChanSw.currentIndexChanged.connect(
            self._fcn_run_switch_location)

    # =====================================================================
    # FILL LOCATION TABLE
    # =====================================================================
    def _get_current_chan_type(self):
        """Return the currently selected channel and detection type."""
        chtp = tuple(str(self._DetectChanSw.currentText()).rsplit(' - '))
        return chtp if len(chtp) == 2 else ('', '')

    def __get_visible_loc(self):
        """Enable/Disable detection table accroding to the visibility."""
        # Get the currently selected channel and type :
        chan, tps = self._get_current_chan_type()
        if chan and tps:
            if tps == 'Peaks':
                viz = self._detect.peaks[(chan, tps)].visible
            else:
                viz = self._detect.line[(chan, tps)].visible
            self._DetectViz.setChecked(viz)
            self._DetectLocations.setEnabled(viz)

    def _fcn_rm_location(self):
        """Remove a detection."""
        # Get the currently selected channel and type :
        chan, types = self._get_current_chan_type()
        # Remove detection :
        if chan and types:
            self._detect.delete(chan, types)
            # Remove vertical indicators :
            pos = np.full((1, 3), -10., dtype=np.float32)
            self._chan.loc[self._channels.index(chan)].set_data(pos=pos)
            # Clean table :
            self._DetectLocations.setRowCount(0)
            # Update GUI :
            self._loc_line_report()
        else:
            self._DetectionTab.setTabEnabled(1, False)
            self._check_detect_menu()

    def _fcn_viz_location(self):
        """Display/hide detections."""
        # Get the currently selected channel and type :
        chan, types = self._get_current_chan_type()
        # Set visibility :
        if chan and types:
            viz = self._DetectViz.isChecked()
            self._detect.visible(viz, chan, types)
            self._chan.loc[self._channels.index(chan)].visible = viz
            self._DetectLocations.setEnabled(viz)

    def _fcn_run_switch_location(self):
        """Run switch location channel and type."""
        # Get the currently selected channel and type :
        chan, types = self._get_current_chan_type()
        if chan and types:
            # Enable/disable the location table :
            self.__get_visible_loc()
            # Find index and durations :
            index = self._detect[(chan, types)]['index']
            # Get durations :
            dur = (index[:, 1] - index[:, 0]) * (1000. / self._sf)
            # Set hypnogram data :
            self._detect.build_hyp(chan, types)
            # Fill location table :
            self._fcn_fill_locations(chan, types, index, dur)

    def _fcn_fill_locations(self, channel, kind, index, duration):
        """Fill the location table."""
        # Disconnect location table :
        self._DetectLocations.disconnect()
        ref = ['Wake', 'N1', 'N2', 'N3', 'REM', 'ART']
        # Clean table :
        self._DetectLocations.setRowCount(0)
        # Get starting index:
        sta_ind, end_ind = index[:, 0], index[:, 1]
        # Define the length of the table:
        self._DetectLocations.setRowCount(min(len(sta_ind), len(duration)))
        # Fill the table :
        for num, (k, j, i) in enumerate(zip(sta_ind, end_ind, duration)):
            # Starting :
            self._DetectLocations.setItem(num, 0, QtWidgets.QTableWidgetItem(
                str(self._time[k])))
            # Ending :
            self._DetectLocations.setItem(num, 1, QtWidgets.QTableWidgetItem(
                str(self._time[j])))
            # Duration :
            self._DetectLocations.setItem(num, 2, QtWidgets.QTableWidgetItem(
                str(i)))
            # Type :
            item = QtWidgets.QTableWidgetItem(ref[int(self._hypno[k])])
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self._DetectLocations.setItem(num, 3, item)
        # Go to the first detected event :
        self._DetectLocations.selectRow(0)
        self._fcn_goto_location()
        # Reconnect :
        self._DetectLocations.itemSelectionChanged.connect(
            self._fcn_goto_location)
        self._DetectLocations.cellChanged.connect(self._fcn_edit_detection)

    # =====================================================================
    # GO TO THE LOCATION
    # =====================================================================
    def _fcn_goto_location(self):
        """Go to the selected row REM / spindles / peak."""
        # Get the currently selected channel and type :
        chan, types = self._get_current_chan_type()
        # Get selected row and channel :
        row = self._DetectLocations.currentRow()
        ix = self._channels.index(chan)
        if row >= 0:
            # Get starting and ending point :
            sta = float(str(self._DetectLocations.item(row, 0).text()))
            end = float(str(self._DetectLocations.item(row, 1).text()))
            # Go to :
            self._SlGoto.setValue(sta)
            # Set vertical lines to the location :
            self._chan.set_location(self._sf, self._data[ix, :], ix, sta, end)

    def _fcn_edit_detection(self):
        """Executed function when the item is edited."""
        # Get the currently selected channel and type :
        chan, types = self._get_current_chan_type()
        # Get selected row and col :
        row = self._DetectLocations.currentRow()
        col = self._DetectLocations.currentColumn()
        val = self._DetectLocations.item(row, col).text()
        if col in [0, 1]:  # Edit starting/ending point
            val = int(np.round(float(val) * self._sf))
            self._detect[(chan, types)]['index'][row, col] = val
        elif col == 2:  # Edit duration
            val = int(np.round(float(val) * self._sf / 1000.))
            start = self._detect[(chan, types)]['index'][row, 0]
            self._detect[(chan, types)]['index'][row, 1] = start + val
        elif col == 3:  # Avoid stage editing
            self._DetectLocations
            self._DetectLocations.setItem(row, 3,
                                          QtWidgets.QTableWidgetItem(val))
        # Update :
        self._loc_line_report(refresh=False)
        self._DetectLocations.selectRow(row)

    def _fcn_rm_selected_event(self):
        """Remove the selected event in the table and update detections."""
        # Get selected row :
        row = self._DetectLocations.currentRow()  # return -1 when no more row
        if row + 1:
            # Remove row :
            self._DetectLocations.removeRow(row)
            # Get the currently selected channel and type :
            chan, types = self._get_current_chan_type()
            # Delete the selected event :
            index = self._detect[(chan, types)]['index']
            if not index.shape[0] - 1:
                self._detect.delete(chan, types)
                # Update :
                self._loc_line_report(refresh=True)
            else:
                self._detect[(chan, types)]['index'] = np.delete(index, row, 0)
                self._loc_line_report(refresh=False)
                self._DetectLocations.selectRow(row)
