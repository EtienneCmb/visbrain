"""Main class for settings managment."""
import numpy as np
import os
import datetime

from PyQt4.QtGui import *
from PyQt4.QtCore import QObjectCleanupHandler, QTimer

import vispy.visuals.transforms as vist

from ....utils import save_hypnoTotxt, save_hypnoToElan, save_hypnoToFig


__all__ = ['uiSettings']


class uiSettings(object):
    """Main class for settings managment."""

    def __init__(self):
        """Init."""
        # =====================================================================
        # MENU & FILES
        # =====================================================================
        # ---------------------- Screenshot ----------------------
        self.actionScreenshot.triggered.connect(self._screenshot)
        self.actionExit.triggered.connect(qApp.quit)

        # ---------------------- Save ----------------------
        self.actionHypnogram_data.triggered.connect(self.saveFile)
        self.actionHypnogram_figure.triggered.connect(self.saveHypFig)
        self.actionInfo_table.triggered.connect(self._fcn_exportInfos)
        self.actionScoring_table.triggered.connect(self._fcn_exportScore)
        self.actionDetection_table.triggered.connect(self._fcn_exportLocation)
        self.actionSaveConfig.triggered.connect(self.saveConfig)

        # ---------------------- Load ----------------------
        self.actionLoadConfig.triggered.connect(self.loadConfig)

        # ---------------------- Shortcut & Doc ----------------------
        self.actionShortcut.triggered.connect(self._fcn_showShortPopup)
        self.actionDocumentation.triggered.connect(self._fcn_openDoc)
        self.actionDownload_pdf_doc.triggered.connect(self._fcn_downloadDoc)

        # =====================================================================
        # SETTINGS PANEL
        # =====================================================================
        # Quick settings panel :
        self.actionQuick_settings.triggered.connect(self._toggle_settings)
        self.q_widget.setVisible(True)

        # =====================================================================
        # SLIDER
        # =====================================================================
        self._slFrame.setMaximumHeight(100)
        # Function applied when the slider move :
        self._slOnStart = False
        self._fcn_sliderSettings()
        self._SlVal.valueChanged.connect(self._fcn_sliderMove)
        # Function applied when slider's settings changed :
        self._SigWin.valueChanged.connect(self._fcn_sliderMove)
        self._SigWin.setKeyboardTracking(False)
        self._SigSlStep.valueChanged.connect(self._fcn_sliderSettings)
        self._SigSlStep.setKeyboardTracking(False)
        # Spin box for window selection :
        self._SlGoto.valueChanged.connect(self._fcn_sliderWinSelection)
        self._SlGoto.setKeyboardTracking(False)
        # Unit conversion :
        self._slRules.currentIndexChanged.connect(self._fcn_sliderMove)
        # Grid toggle :
        self._slGrid.clicked.connect(self._fcn_gridToggle)
        # Text format :
        self._slTxtFormat = "Window : [ {start} ; {end} ] {unit} || " + \
                            "Sleep stage : {conv}"
        # Absolute time :
        self._slAbsTime.clicked.connect(self._fcn_sliderMove)
        # Magnify :
        self._slMagnify.clicked.connect(self._fcn_sliderMagnify)

        # =====================================================================
        # ZOOMING
        # =====================================================================
        self._PanHypZoom.clicked.connect(self._fcn_Zooming)
        self._PanSpecZoom.clicked.connect(self._fcn_Zooming)
        self._PanTimeZoom.clicked.connect(self._fcn_Zooming)

    # =====================================================================
    # MENU & FILE MANAGMENT
    # =====================================================================
    def _fcn_showShortPopup(self):
        """Open shortcut window."""
        self._shpopup.show()

    def _fcn_openDoc(self):
        """Open documentation."""
        import webbrowser
        webbrowser.open('http://etiennecmb.github.io/visbrain/sleep.html')

    def _fcn_downloadDoc(self):
        """Open documentation."""
        import webbrowser
        webbrowser.open("https://drive.google.com/file/d/"
                        "0B6vtJiCQZUBvNFJMTER3SERGUW8/view?usp=sharing")

    # =====================================================================
    # SCREENSHOT
    # =====================================================================
    def _screenshot(self):
        """Screenshot using the GUI."""
        # self.setFixedSize(100, 100)
        # Get filename :
        filename = QFileDialog.getSaveFileName(self, 'Screenshot',
                                               'screenshot', "PNG (*.PNG);;"
                                               "TIFF (*.tiff);;JPG (*.jpg);;"
                                               "All files (*.*)")
        filename = str(filename)  # py2
        # Screnshot function :
        def _takeScreenShot():
            """Take the screenshot."""
            file, ext = os.path.splitext(filename)
            # p = QPixmap.grabWidget(self.centralwidget)
            p = QPixmap.grabWindow(self.centralwidget.winId())
            p.save(file + '.png')
        # Take screenshot if filename :
        if filename:
            # Timer (avoid shooting the saving window)
            self.timerScreen = QTimer()
            # self.timerScreen.setInterval(100)
            self.timerScreen.setSingleShot(True)
            self.timerScreen.timeout.connect(_takeScreenShot)
            self.timerScreen.start(500)

    def _toggle_settings(self):
        """Toggle method for display / hide the settings panel."""
        self.q_widget.setVisible(not self.q_widget.isVisible())

    def saveFile(self):
        """Save the hypnogram."""
        filename = QFileDialog.getSaveFileName(self, 'Save File', 'hypno',
                                               "Text file (*.txt);;Elan file "
                                               "(*.hyp);;All files (*.*)")
        filename = str(filename)  # py2
        if filename:
            file, ext = os.path.splitext(filename)

            # Switch between differents types :
            if ext == '.hyp':
                save_hypnoToElan(filename, self._hypno, self._sf, self._sfori,
                                 self._N)
            elif ext == '.txt':
                save_hypnoTotxt(filename, self._hypno, self._sf, self._sfori,
                                self._N, 1)
            else:
                raise ValueError("Not a valid extension")

    def saveHypFig(self):
        """Save a 600 dpi .png figure of the hypnogram."""
        filename = QFileDialog.getSaveFileName(self, 'Save Hypnogram figure',
                                               'hypno.png', "PNG (*.png)")
        filename = str(filename)  # py2
        if filename:
            save_hypnoToFig(filename, self._hypno, self._sf, self._toffset)

    def saveConfig(self):
        """Save a config file (*.txt) containing several display parameters."""
        import json
        upath = os.path.split(self._file)[0]
        filename = QFileDialog.getSaveFileName(self, 'Save config file',
                                               upath, "Text file (*.txt)")
        filename = str(filename)  # py2
        if filename:
            with open(filename, 'w') as f:
                config = {}
                viz = []
                amp = []
                for i, k in enumerate(self._chanChecks):
                    viz.append(k.isChecked())
                    amp.append(self._ymaxSpin[i].value())

                config['Channel_Names'] = self._channels
                config['Channel_Visible'] = viz
                config['Channel_Amplitude'] = amp
                config['Spec_Visible'] = self._PanSpecViz.isChecked()
                config['Spec_Length'] = self._PanSpecNfft.value()
                config['Spec_Overlap'] = self._PanSpecStep.value()
                config['Spec_Cmap'] = self._PanSpecCmap.currentIndex()
                config['Spec_Chan'] = self._PanSpecChan.currentIndex()
                config['Spec_Fstart'] = self._PanSpecFstart.value()
                config['Spec_Fend'] = self._PanSpecFend.value()
                config['Spec_Con'] = self._PanSpecCon.value()
                config['Hyp_Visible'] = self._PanHypViz.isChecked()
                config['Time_Visible'] = self._PanTimeViz.isChecked()
                json.dump(config, f)

    def loadConfig(self):
        """Load a config file (*.txt) containing several display parameters."""
        import json
        if hasattr(self, '_config_file'):
            filename = str(self._config_file)
        else:
            upath = os.path.split(self._file)[0]
            filename = QFileDialog.getOpenFileName(
                self, "Open config file", upath, "Text file (*.txt)")
            filename = str(filename)  # py2

        with open(filename) as f:
            config = json.load(f)
            # Channels
            for i, k in enumerate(self._chanChecks):
                self._chanChecks[i].setChecked(config['Channel_Visible'][i])
                self._ymaxSpin[i].setValue(config['Channel_Amplitude'][i])

            # Spectrogram
            self._PanSpecViz.setChecked(config['Spec_Visible'])
            self._PanSpecNfft.setValue(config['Spec_Length'])
            self._PanSpecStep.setValue(config['Spec_Overlap'])
            self._PanSpecCmap.setCurrentIndex(config['Spec_Cmap'])
            self._PanSpecChan.setCurrentIndex(config['Spec_Chan'])
            self._PanSpecFstart.setValue(config['Spec_Fstart'])
            self._PanSpecFend.setValue(config['Spec_Fend'])
            self._PanSpecCon.setValue(config['Spec_Con'])

            # Hypnogram & Time axis
            self._PanHypViz.setChecked(config['Hyp_Visible'])
            self._PanTimeViz.setChecked(config['Time_Visible'])

            # Update display
            self._fcn_chanViz()
            self._fcn_chanAmplitude()
            self._fcn_specViz()
            self._fcn_specSetData()
            self._fcn_hypViz()
            self._fcn_timeViz()

    # =====================================================================
    # SLIDER
    # =====================================================================
    def _fcn_sliderMove(self):
        """Function applied when the slider move."""
        # ================= INDEX =================
        # Get slider variables :
        val = self._SlVal.value()
        step = self._SigSlStep.value()
        win = self._SigWin.value()
        xlim = (val*step, val*step+win)
        specZoom = self._PanSpecZoom.isChecked()
        hypZoom = self._PanHypZoom.isChecked()
        timeZoom = self._PanTimeZoom.isChecked()
        unit = str(self._slRules.currentText())

        # Find closest time index :
        t = [0, 0]
        t[0] = int(round(np.abs(self._time - xlim[0]).argmin()))
        t[1] = int(round(np.abs(self._time - xlim[1]).argmin()))

        # ================= MESH UPDATES =================
        # ---------------------------------------
        # Update display signal :
        sl = slice(t[0], t[1])
        self._chan.set_data(self._sf, self._data, self._time, sl=sl,
                            ylim=self._ylims)

        # ---------------------------------------
        # Update spectrogram indicator :
        if self._PanSpecIndic.isEnabled() and not specZoom:
            ylim = (self._PanSpecFstart.value(), self._PanSpecFend.value())
            self._specInd.set_data(xlim=xlim, ylim=ylim)

        # ---------------------------------------
        # Update hypnogram indicator :
        if self._PanHypIndic.isEnabled() and not hypZoom:
            self._hypInd.set_data(xlim=xlim, ylim=(-6., 2.))

        # ---------------------------------------
        # Update topoplot if visible :
        if self._topoW.isVisible():
            self._topo.set_data(self._sf, self._time[sl], self._data[:, sl])

        # ---------------------------------------
        # Update Time indicator :
        if self._PanTimeIndic.isEnabled():
            self._TimeAxis.set_data(xlim[0], win, self._time, unit=unit)

        # ================= GUI =================
        # Update Go to :
        self._SlGoto.setValue(val*step)

        # ================= ZOOMING =================
        # Histogram :
        if hypZoom:
            self._hypcam.rect = (xlim[0], -5, xlim[1]-xlim[0], 7.)

        # Spectrogram :
        if specZoom:
            self._speccam.rect = (xlim[0], self._spec.freq[0], xlim[1]-xlim[0],
                                  self._spec.freq[-1] - self._spec.freq[0])

        # Time axis :
        if timeZoom:
            self._TimeAxis.set_data(xlim[0], win, np.array([xlim[0], xlim[1]]),
                                    unit='seconds')
            self._timecam.rect = (xlim[0], 0., win, 1.)

        # ================= TEXT INFO =================
        hypref = int(self._hypno[t[0]])
        hypconv = self._hconv[hypref]
        hypcol = self._hypcolor[hypconv]
        stage = str(self._hypYLabels[hypconv + 1].text())
        # Get unit and convert:
        if self._slAbsTime.isChecked():
            xlim = np.asarray(xlim) + self._toffset
            start = str(datetime.datetime.utcfromtimestamp(
                                                       xlim[0])).split(' ')[1]
            stend = str(datetime.datetime.utcfromtimestamp(
                                                       xlim[1])).split(' ')[1]
            txt = "Window : [ " + start + " ; " + stend + " ] || Sleep " + \
                "stage : " + stage
        else:
            unit = self._slRules.currentText()
            if unit == 'seconds':
                fact = 1.
            elif unit == 'minutes':
                fact = 60.
            elif unit == 'hours':
                fact = 3600.
            xconv = np.round((1000*xlim[0]/fact, 1000*xlim[1]/fact))/1000
            # Format string :
            txt = self._slTxtFormat.format(start=str(xconv[0]),
                                           end=str(xconv[1]), unit=unit,
                                           conv=stage)
        # Set text :
        self._SlText.setText(txt)
        self._SlText.setFont(self._font)
        self._SlText.setStyleSheet("QLabel {color: " +
                                   hypcol + ";}")

        # ================= HYPNO LABELS =================
        for k in self._hypYLabels:
            k.setStyleSheet("QLabel")
        self._hypYLabels[hypconv + 1].setStyleSheet("QLabel {color: " +
                                                    hypcol+";}")

    def _fcn_sliderSettings(self):
        """Function applied to change slider settings."""
        # Get current slider value :
        sl = self._SlVal.value()
        slmax = self._SlVal.maximum()
        win = self._SigWin.value()
        # Set minimum :
        self._SlVal.setMinimum(self._time.min())
        # Set maximum :
        step = self._SigSlStep.value()
        self._SlVal.setMaximum(((self._time.max() - win)/step) + 1)
        self._SlVal.setTickInterval(step)
        self._SlVal.setSingleStep(step)
        self._SlGoto.setMaximum((self._time.max() - win))
        # Re-set slider value :
        self._SlVal.setValue(sl * self._SlVal.maximum() / slmax)

        if self._slOnStart:
            self._fcn_sliderMove()
            # Update grid :
            if self._PanHypZoom.isChecked():
                self._hyp.set_grid(self._time, step)
            else:
                self._hyp.set_grid(self._time, win)
        else:
            self._slOnStart = True

    def _fcn_sliderWinSelection(self):
        """Move slider using window spin."""
        self._SlVal.setValue(self._SlGoto.value() / self._SigSlStep.value())

    def _fcn_sliderMagnify(self):
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
    def _fcn_gridToggle(self):
        """Toggle grid visibility."""
        viz = self._slGrid.isChecked()
        # Toggle hypno grid :
        self._hyp.grid.visible = viz
        # Toggle grid for each channel :
        for k in self._chan.grid:
            k.visible = viz

    # =====================================================================
    # RULER
    # =====================================================================
    def _get_factFromUnit(self):
        """Get factor conversion from current selected unit."""
        unit = str(self._slRules.currentText())
        if unit == 'seconds':
            fact = 1.
        elif unit == 'minutes':
            fact = 60.
        elif unit == 'hours':
            fact = 3600.
        return fact

    # =====================================================================
    # ZOOMING
    # =====================================================================
    def _fcn_Zooming(self):
        """Apply dynamic zoom on hypnogram."""
        # Hypnogram :
        if self._PanHypZoom.isChecked():
            self._PanHypIndic.setEnabled(False)
            self._hypInd.mesh.visible = False
        else:
            self._PanHypIndic.setEnabled(True)
            self._hypcam.rect = (self._time.min(), -5.,
                                 self._time.max() - self._time.min(), 7.)
            self._hypInd.mesh.visible = self._PanHypIndic.isChecked()

        # Spectrogram :
        if self._PanSpecZoom.isChecked():
            self._PanSpecIndic.setEnabled(False)
            self._specInd.mesh.visible = False
        else:
            self._PanSpecIndic.setEnabled(True)
            self._speccam.rect = (self._time.min(), self._spec.freq[0],
                                  self._time.max() - self._time.min(),
                                  self._spec.freq[-1] - self._spec.freq[0])
            self._specInd.mesh.visible = self._PanSpecIndic.isChecked()
        # Time axis :
        if self._PanTimeZoom.isChecked():
            # self._PanTimeIndic.setChecked(False)
            self._PanTimeIndic.setEnabled(False)
            self._TimeAxis.mesh.visible = False
        else:
            self._PanTimeIndic.setEnabled(True)
            self._timecam.rect = (self._time.min(), 0.,
                                  self._time.max() - self._time.min(), 1.)
            self._TimeAxis.mesh.visible = self._PanTimeIndic.isChecked()

        self._fcn_sliderSettings()

    def on_mouse_wheel(self, event):
        """Executed function on mouse wheel."""
        self._SlVal.setValue(self._SlVal.value() + event.delta[1])

    # =====================================================================
    # HYPNO
    # =====================================================================
    def _add_stage_on_win(self, stage):
        """Change the stage on the current window."""
        # Get the window :
        win = self._SigWin.value()
        val = self._SlVal.value()
        step = self._SigSlStep.value()
        xlim = (val*step, val*step+win)
        # Find closest time index :
        t = [0, 0]
        t[0] = int(round(np.abs(self._time - xlim[0]).argmin()))
        t[1] = int(round(np.abs(self._time - xlim[1]).argmin()))
        # Set the stage :
        self._hypno[t[0]:t[1]] = stage
        self._hyp.set_data(self._sf, self._hypno, self._time)
        # Update info table :
        self._fcn_infoUpdate()
        # Update scoring table :
        self._fcn_Hypno2Score()
        self._fcn_Score2Hypno()

    # =====================================================================
    # CLEAN / RESET GUI
    # =====================================================================
    def _fcn_cleanGui(self):
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

    def _fcn_resetGui(self):
        """Reset the GUI."""
        from .uiElements import uiElements
        from ...visuals import visuals
        from ...tools import Tools
        uiElements.__init__(self)
        self._camCreation()
        visuals.__init__(self)
        Tools.__init__(self)
        self._fcnsOnCreation()
