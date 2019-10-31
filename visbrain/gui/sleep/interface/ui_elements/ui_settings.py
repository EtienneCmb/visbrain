"""Main class for settings managment."""
import numpy as np
import datetime
from PyQt5.QtCore import QObjectCleanupHandler

import vispy.visuals.transforms as vist


class UiSettings(object):
    """Main class for settings managment."""

    def __init__(self):
        """Init."""
        # =====================================================================
        # SLIDER
        # =====================================================================
        self._slFrame.setMaximumHeight(100)
        # Function applied when the slider move :
        self._slOnStart = False
        self._fcn_slider_settings()
        self._SlVal.valueChanged.connect(self._fcn_slider_move)
        # Function applied when the display window changed :
        self._SigWin.valueChanged.connect(self._fcn_sigwin_settings)
        self._SigWin.setKeyboardTracking(False)
        # Function applied when the scoring window changed :
        self._ScorWin.valueChanged.connect(self._fcn_scorwin_settings)
        self._ScorWin.setKeyboardTracking(False)
        # Function applied when the slider settings changed
        self._SigSlStep.valueChanged.connect(self._fcn_slider_settings)
        self._SigSlStep.setKeyboardTracking(False)
        # Spin box for window selection :
        self._SlGoto.valueChanged.connect(self._fcn_slider_win_selection)
        self._SlGoto.setKeyboardTracking(False)
        # Unit conversion :
        self._slRules.currentIndexChanged.connect(self._fcn_slider_move)
        # Grid toggle :
        self._slGrid.clicked.connect(self._fcn_grid_toggle)
        # Text format :
        self._slTxtFormat = "Window : [ {start} ; {end} ] {unit} || " + \
                            "Scoring : [ {start_scor} ; {end_scor} ] {unit} || " + \
                            "Sleep stage : {conv}"
        # Absolute time :
        self._slAbsTime.clicked.connect(self._fcn_slider_move)
        # Magnify :
        self._slMagnify.clicked.connect(self._fcn_slider_magnify)
        # Visible scoring window indicator :
        self._ScorWinVisible.clicked.connect(self._fcn_scorwin_indicator_toggle)
        # Lock scoring window to the display window
        self._LockScorSigWins.clicked.connect(self._fcn_lock_scorwin_sigwin)
        # Annotation from the navigation bar :
        self._AnnotateRun.clicked.connect(self._fcn_annotate_nav)

    @staticmethod
    def _scoring_window_xlim(xlim, scorwin):
        """Define scoring window xlim from scoring window size and SigWin."""
        xhalf = (xlim[1] - xlim[0])/2 + xlim[0]
        return (
            max(xlim[0], xhalf - scorwin/2),
            min(xlim[1], xhalf + scorwin/2)
        ) # Centered to display window

    # =====================================================================
    # SLIDER, DISPLAY WINDOW AND SCORING WINDOW
    # =====================================================================
    def _update_text_info(self, xlim, xlim_scor, hypcol, stage):
        # Get unit and convert:
        if self._slAbsTime.isChecked():
            xlim = np.asarray(xlim) + self._toffset
            start = str(datetime.datetime.utcfromtimestamp(
                xlim[0])).split(' ')[1]
            stend = str(datetime.datetime.utcfromtimestamp(
                xlim[1])).split(' ')[1]
            start_scor = str(datetime.datetime.utcfromtimestamp(
                xlim_scor[0])).split(' ')[1]
            stend_scor = str(datetime.datetime.utcfromtimestamp(
                xlim_scor[1])).split(' ')[1]
            txt = "Window : [ " + start + " ; " + stend + " ] || " + \
                "Scoring : [ " + start_scor + " ; " + stend_scor + " ] || " + \
                "Sleep stage : " + stage
        else:
            unit = self._slRules.currentText()
            if unit == 'seconds':
                fact = 1.
            elif unit == 'minutes':
                fact = 60.
            elif unit == 'hours':
                fact = 3600.
            xconv = np.round(1000. * np.array(xlim) / fact) / 1000.
            xconv_scor = np.round(1000. * np.array(xlim_scor) / fact) / 1000.
            # Format string :
            txt = self._slTxtFormat.format(
                start=str(xconv[0]), end=str(xconv[1]),
                start_scor=str(xconv_scor[0]), end_scor=str(xconv_scor[1]),
                unit=unit,
                conv=stage)
        # Set text :
        self._SlText.setText(txt)
        self._SlText.setFont(self._font)
        self._SlText.setStyleSheet("QLabel {color: " +
                                   hypcol + ";}")

    def _update_scorwin_indicator(self):
        # Get scoring window x_start x_end
        val = self._SlVal.value()
        step = self._SigSlStep.value()
        win = self._SigWin.value()
        xlim = (val * step, val * step + win)
        scorwin = self._ScorWin.value()
        xlim_scor = self._scoring_window_xlim(xlim, scorwin)
        # Move bars
        for i, chan in self._chan:
            self._chan.scorwin_ind[i].set_data(xlim_scor[0], xlim_scor[1],
                                               self._ylims[i, :])

    def _fcn_slider_move(self):
        """Function applied when the slider move."""
        # ================= INDEX =================
        # Get slider variables :
        val = self._SlVal.value()
        step = self._SigSlStep.value()
        win = self._SigWin.value()
        xlim = (val * step, val * step + win)
        scorwin = self._ScorWin.value()
        xlim_scor = self._scoring_window_xlim(xlim, scorwin)
        iszoom = self.menuDispZoom.isChecked()
        unit = str(self._slRules.currentText())
        # Find closest time index :
        t = [0, 0]
        t[0] = int(round(np.abs(self._time - xlim[0]).argmin()))
        t[1] = int(round(np.abs(self._time - xlim[1]).argmin()))
        # Hypnogram info :
        hypref = int(self._hypno[t[0]])
        hypconv = self._hconv[hypref]
        hypcol = self._hypcolor[hypconv]
        stage = str(self._hypYLabels[hypconv + 2].text())

        # ================= MESH UPDATES =================
        # ---------------------------------------
        # Update display signal :
        sl = slice(t[0], t[1])
        self._chan.set_data(self._sf, self._data, self._time, sl=sl,
                            ylim=self._ylims)
        # Redraw the scoring window indicators
        self._update_scorwin_indicator()

        # Update display signal on window histogram (move camera)
        self._winhyp.set_rect_x(*xlim)

        # ---------------------------------------
        is_indic_checked = self.menuDispIndic.isChecked()
        # Update spectrogram indicator :
        if is_indic_checked and not iszoom:
            ylim = (self._PanSpecFstart.value(), self._PanSpecFend.value())
            self._specInd.set_data(xlim=xlim, ylim=ylim)

        # ---------------------------------------
        # Update hypnogram indicator :
        if is_indic_checked and not iszoom:
            self._hypInd.set_data(xlim=xlim, ylim=(-6., 2.))

        # ---------------------------------------
        # Update topoplot if visible :
        if self._topoW.isVisible():
            # Prepare data before plotting :
            data = self._topo._prepare_data(self._sf, self._data[:, sl],
                                            self._time[sl]).mean(1)
            # Set preprocessed sleep data :
            self._topo.set_sleep_topo(data)
            # Update title :
            fm, fh = self._PanTopoFmin.value(), self._PanTopoFmax.value()
            dispas = self._PanTopoDisp.currentText()
            txt = 'Mean ' + dispas + ' in\n[' + str(fm) + ';' + str(fh) + 'hz]'
            self._topoTitle.setText(txt)
            self._topoTitle.setStyleSheet("QLabel {color: " +
                                          hypcol + ";}")

        # ---------------------------------------
        # Update Time indicator :
        if is_indic_checked:
            self._TimeAxis.set_data(xlim[0], win, self._time, unit=unit,
                                    markers=self._annot_mark)

        # ================= GUI =================
        # Update Go to :
        self._SlGoto.setValue(val * step)

        # ================= ZOOMING =================
        if iszoom:
            xlim_diff = xlim[1] - xlim[0]
            # Histogram :
            self._hypcam.rect = (xlim[0], -5, xlim_diff, 7.)
            # Spectrogram :
            self._speccam.rect = (xlim[0], self._spec.freq[0], xlim_diff,
                                  self._spec.freq[-1] - self._spec.freq[0])
            # Time axis :
            self._TimeAxis.set_data(xlim[0], win, np.array([xlim[0], xlim[1]]),
                                    unit='seconds', markers=self._annot_mark)
            self._timecam.rect = (xlim[0], 0., win, 1.)

        # ================= TEXT INFO =================
        self._update_text_info(xlim, xlim_scor, hypcol, stage)

        # ================= HYPNO LABELS =================
        for k in self._hypYLabels:
            k.setStyleSheet("QLabel")
        self._hypYLabels[hypconv + 2].setStyleSheet("QLabel {color: " +
                                                    hypcol + ";}")

    def _fcn_slider_settings(self):
        """Function applied to change slider settings."""
        # Get current slider value :
        sl = self._SlVal.value()
        slmax = self._SlVal.maximum()
        win = self._SigWin.value()
        # Set minimum :
        self._SlVal.setMinimum(self._time.min())
        # Set maximum :
        step = self._SigSlStep.value()
        self._SlVal.setMaximum(((self._time.max() - win) / step) + 1)
        self._SlVal.setTickInterval(step)
        self._SlVal.setSingleStep(step)
        self._SlGoto.setMaximum((self._time.max() - win))
        # Re-set slider value :
        self._SlVal.setValue(sl * self._SlVal.maximum() / slmax)

        if self._slOnStart:
            self._fcn_slider_move()
            # Update grid :
            if self.menuDispZoom.isChecked():
                self._hyp.set_grid(self._time, step)
            else:
                self._hyp.set_grid(self._time, win)
        else:
            self._slOnStart = True

    def _fcn_sigwin_settings(self):
        """Function applied when changing the display window size."""
        # Change maximum allowed value of the scoring window
        win = self._SigWin.value()
        self._ScorWin.setMaximum(win)
        # In "Lock" mode
        if self._LockScorSigWins.isChecked():
            # Change the scoring window value without unlocking
            self._ScorWin.blockSignals(True)
            self._ScorWin.setValue(win)
            self._ScorWin.blockSignals(False)
            # Change the slider step size
            self._SigSlStep.setValue(win)
        # Redraw stuff as if we were moving the slider
        self._fcn_slider_move()

    def _fcn_scorwin_settings(self):
        """Function applied when changing the scoring window size."""
        ## Unlock the scoring window
        self._LockScorSigWins.setChecked(False)
        ## Make the scoring window visible
        self._ScorWinVisible.setChecked(True)
        self._fcn_scorwin_indicator_toggle()
        ## Change value of slider step to make it equal to the scoring window
        scorwin = self._ScorWin.value()
        self._SigSlStep.setValue(scorwin)
        ## Change the text info:
        # Gather values of parameters of interest
        # Slider/windows 
        val = self._SlVal.value()
        step = self._SigSlStep.value()
        win = self._SigWin.value()
        xlim = (val * step, val * step + win)
        scorwin = self._ScorWin.value()
        xlim_scor = self._scoring_window_xlim(xlim, scorwin)
        # Find closest time index :
        t = [0, 0]
        t[0] = int(round(np.abs(self._time - xlim[0]).argmin()))
        t[1] = int(round(np.abs(self._time - xlim[1]).argmin()))
        # hypnogram
        hypref = int(self._hypno[t[0]])
        hypconv = self._hconv[hypref]
        hypcol = self._hypcolor[hypconv]
        stage = str(self._hypYLabels[hypconv + 2].text())
        self._update_text_info(xlim, xlim_scor, hypcol, stage)
        ## Redraw the scoring window indicator bars
        self._update_scorwin_indicator()

    def _fcn_slider_win_selection(self):
        """Move slider using window spin."""
        self._SlVal.setValue(self._SlGoto.value() / self._SigSlStep.value())

    def _fcn_slider_magnify(self):
        """Magnify signals."""
        # Set transformation to each node parent :
        for k in self._chan.node:
            # Use either Magnify / Null transformation :
            if self._slMagnify.isChecked():
                transform = vist.nonlinear.Magnify1DTransform()
            else:
                transform = vist.NullTransform()
            k.transform = transform

    # =====================================================================
    # GRID
    # =====================================================================
    def _fcn_grid_toggle(self):
        """Toggle grid visibility."""
        viz = self._slGrid.isChecked()
        # Toggle hypno grid :
        self._hyp.grid.visible = viz
        # Toggle grid for each channel :
        for k in self._chan.grid:
            k.visible = viz

    # =====================================================================
    # DISPLAY SCORING WINDOW INDICATOR BARS
    # =====================================================================
    def _fcn_scorwin_indicator_toggle(self):
        """Toggle visibility of scoring window indicators."""
        viz = self._ScorWinVisible.isChecked()
        for i, chan in self._chan:
            self._chan.scorwin_ind[i].mesh_start.visible = viz
            self._chan.scorwin_ind[i].mesh_end.visible = viz

    # =====================================================================
    # LOCK SCORING WINDOW TO DISPLAY WINDOW
    # =====================================================================
    def _fcn_lock_scorwin_sigwin(self):
        """Toggle locking of scoring window to display window."""
        locked = self._LockScorSigWins.isChecked()
        # If locking
        if locked:
            # Set _ScorWin to _SigWin
            self._ScorWin.setValue(self._SigWin.value())
            # Hide the scoring window indicators
            self._ScorWinVisible.setChecked(False)
            self._fcn_scorwin_indicator_toggle()
        # If unlocking
        else:
            # Show the scoring window
            self._ScorWinVisible.setChecked(True)
            self._fcn_scorwin_indicator_toggle()

    # =====================================================================
    # RULER
    # =====================================================================
    def _get_fact_from_unit(self):
        """Get factor conversion from current selected unit."""
        unit = str(self._slRules.currentText())
        if unit == 'seconds':
            fact = 1.
        elif unit == 'minutes':
            fact = 60.
        elif unit == 'hours':
            fact = 3600.
        return fact

    def on_mouse_wheel(self, event):
        """Executed function on mouse wheel."""
        self._SlVal.setValue(self._SlVal.value() + event.delta[1])

    # =====================================================================
    # HYPNO
    # =====================================================================
    def _add_stage_on_scorwin(self, stage):
        """Change the stage on the current scoring window."""
        # Get the window :
        win = self._SigWin.value()
        val = self._SlVal.value()
        step = self._SigSlStep.value()
        xlim = (val * step, val * step + win)
        # Get the scoring window :
        scorwin = self._ScorWin.value()
        xlim_scor = self._scoring_window_xlim(xlim, scorwin)
        # Find closest time index :
        t = [0, 0]
        t[0] = int(round(np.abs(self._time - xlim_scor[0]).argmin()))
        t[1] = int(round(np.abs(self._time - xlim_scor[1]).argmin()))
        # Set the stage :
        self._hypno[t[0]:t[1]] = stage
        self._set_hyp_stage(t[0], t[1], stage)
        # # Update info table :
        self._fcn_info_update()
        # Update scoring table :
        self._fcn_hypno_to_score()
        # self._fcn_score_to_hypno()

    def _set_hyp_stage(self, *args, **kwargs):
        self._hyp.set_stage(*args, **kwargs)
        self._winhyp.set_stage(*args, **kwargs)


    # =====================================================================
    # Annotate
    # =====================================================================
    def _fcn_annotate_nav(self):
        """Annotate from the selected window."""
        # Set the current tab to the annotation tab :
        self.QuickSettings.setCurrentIndex(5)
        # Run annotation :
        self._fcn_annotate_add('')

    # =====================================================================
    # CLEAN / RESET GUI
    # =====================================================================
    def _fcn_clean_gui(self):
        """Clean the entire GUI."""
        # -------------- TABLES --------------
        # Info :
        self._infoTable.clear()
        self._infoTable.setRowCount(0)

        # Detection :
        self._DetectLocations.clear()
        self._DetectLocations.setRowCount(0)

        # -------------- LIST BOX --------------
        # Disconnect :
        self._PanSpecChan.currentIndexChanged.disconnect()
        # Clear items :
        self._PanSpecChan.clear()
        self._ToolDetectChan.clear()

        # -------------- VISUALS --------------
        # Channels :
        for k in range(len(self)):
            # Disconnect buttons :
            self._chanChecks[k].clicked.disconnect()
            self._yminSpin[k].valueChanged.disconnect()
            self._ymaxSpin[k].valueChanged.disconnect()
            # Delete elements :
            self._chanChecks[k].deleteLater()
            self._yminSpin[k].deleteLater(), self._ymaxSpin[k].deleteLater()
            self._chanWidget[k].deleteLater()
            self._chanLayout[k].deleteLater()
            self._chanLabels[k].deleteLater()
            self._amplitudeTxt[k].deleteLater()
            self._chanCanvas[k].parent = None
        QObjectCleanupHandler().add(self._chanGrid)
        QObjectCleanupHandler().clear()
        # Spectrogram :
        self._specCanvas.parent = None
        self._SpecW.deleteLater(), self._SpecLayout.deleteLater()
        self._specLabel.deleteLater()
        # Hypnogram :
        self._hypCanvas.parent = None
        self._HypW.deleteLater(), self._HypLayout.deleteLater()
        self._hypLabel.deleteLater()
        # Time axis :
        self._TimeAxis.parent = None
        self._TimeAxisW.deleteLater(), self._TimeLayout.deleteLater()
        self._timeLabel.deleteLater()

    def _fcn_reset_gui(self):
        """Reset the GUI."""
        from .uiElements import uiElements
        from ...visuals import visuals
        from ...tools import Tools
        uiElements.__init__(self)
        self._cam_creation()
        visuals.__init__(self)
        Tools.__init__(self)
        self._fcns_on_creation()
