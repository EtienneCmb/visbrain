"""Main class for settings managment."""
import numpy as np
import os

from PyQt4.QtGui import *


__all__ = ['uiSettings']


class uiSettings(object):
    """Main class for settings managment."""

    def __init__(self):
        """Init."""
        # =====================================================================
        # MENU & FILES
        # =====================================================================
        # ------------------------------- FILE -------------------------------
        # Screenshot :
        screenshot = QAction("Screenshot", self)
        screenshot.setShortcut("Ctrl+N")
        screenshot.triggered.connect(self._screenshot)
        self.menuFiles.addAction(screenshot)

        # Save :
        save = QAction("Save hypnogram", self)
        save.setShortcut("Ctrl+S")
        save.triggered.connect(self.saveFile)
        self.menuFiles.addAction(save)

        # Load :
        openm = QAction("Load", self)
        openm.setShortcut("Ctrl+O")
        openm.triggered.connect(self.openFile)
        self.menuFiles.addAction(openm)

        # Quit :
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        self.menuFiles.addAction(exitAction)

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
        self._slTxtFormat = "Window: [ {start} ; {end} ] {unit} || " + \
                            "Sleep stage: {conv}"

        # =====================================================================
        # ZOOMING
        # =====================================================================
        self._PanHypZoom.clicked.connect(self._fcn_Zooming)
        self._PanSpecZoom.clicked.connect(self._fcn_Zooming)
        self._PanTimeZoom.clicked.connect(self._fcn_Zooming)

    # =====================================================================
    # MENU & FILE MANAGMENT
    # =====================================================================
    def saveFile(self):
        """Save the hypnogram."""
        filename = QFileDialog.getSaveFileName(self, 'Save File',
                                               os.path.join(os.getenv('HOME'),
                                                            'hypno.txt'),
                                               "Text file (*.txt);;Elan file "
                                               "(*.hyp);;All files (*.*)")

        if filename:
            file, ext = os.path.splitext(filename)

            # Switch between differents types :
            if ext == '.hyp':
                self._save_hypno_elan(filename, self._hypno, self._sf)

            elif ext == '.txt':
                self._save_hypno_txt(filename, self._hypno, self._sf, 1)

            else:
                raise ValueError("Not a valid extension")

    def _save_hypno_elan(self, filename, hypno, sf):
        """Save hypnogram in Elan file format (*.hyp).

        Args:
            filename: str
                Filename (with full path) of the file to save

            hypno: np.ndarray
                Hypnogram array, same length as data

            sf: int
                Sampling frequency of the data (after downsampling)
        """
        hdr = np.array([['time_base 1.000000'],
                        ['sampling_period ' + str(round(1/sf, 8))],
                        ['epoch_nb ' + str(int(hypno.size / sf))],
                        ['epoch_list']]).flatten()

        # Check data format
        sf = int(sf)
        hypno = hypno.astype(int)
        # Save
        export = np.append(hdr, hypno[::sf].astype(str))
        np.savetxt(filename, export, fmt='%s')

    def _save_hypno_txt(self, filename, hypno, sf, window=1.):
        """Save hypnogram in txt file format (*.txt).

        Header is in file filename_description.txt

        Args:
            filename: str
                Filename (with full path) of the file to save

            hypno: np.ndarray
                Hypnogram array, same length as data

            sf: float
                Sampling frequency of the data (after downsampling)

        Kargs:
            window: float, optional, (def 1)
                Time window (second) of each point in the hypno
                Default is one value per second
                (e.g. window = 30 = 1 value per 30 second)
        """
        base = os.path.basename(filename)
        dirname = os.path.dirname(filename)
        descript = os.path.join(dirname,
                                os.path.splitext(base)[0] + '_description.txt')

        # Save hypno
        ds_fac = int(sf * window)
        np.savetxt(filename, hypno[::ds_fac].astype(int), fmt='%s')

        # Save header file
        hdr = np.array([['time ' + str(window)], ['W 0'], ['N1 1'], ['N2 2'],
                        ['N3 3'], ['REM 4'], ['Art -1']]).flatten()
        np.savetxt(descript, hdr, fmt='%s')

    def openFile(self):
        """
        """
        raise ValueError("NOT CONFIGURED")
        # filename = QFileDialog.getSaveFileName(self, 'Open File',
        #                                        os.getenv('HOME'))
        # f = open(filename, 'w')
        # filedata = self.text.toPlainText()
        # f.write(filedata)
        # f.close()

    def _fcn_panSettingsViz(self):
        """
        """
        pass

    def _fcn_CanVisToggle(self):
        """Toggle the different panel."""
        self._NdVizPanel.setVisible(self._CanVisNd.isChecked())
        self._1dVizPanel.setVisible(self._CanVis1d.isChecked())
        # self._ImVizPanel.setVisible(self._CanVis1d.isChecked())

    def _fcn_QuickTabSelec(self):
        """On Quick settings tab selection.

        Triggered function when the user select a tab from the QuickSettings
        Tab widget.
        """
        pass
        # if self.QuickSettings.currentIndex() == 1:
        #     self._fcn_ndAxis_update()
        # if self.QuickSettings.currentIndex() == 2:
        #     self._fcn_1dAxis_update()
        # elif self.QuickSettings.currentIndex() == 3:
        #     self._fcn_imAxis_update()
        # pass

    def _fcn_1dPltTabSelect(self):
        """On Inspect tab selection.

        Triggered function when the user select a tab from the Inspect
        Tab widget.
        """
        if self._1dPltTab.currentIndex() == 0:
            self._fcn_1dAxis_update()
        elif self._1dPltTab.currentIndex() == 1:
            self._fcn_imAxis_update()

    # =====================================================================
    # GUI
    # =====================================================================
    def _screenshot(self):
        """Screenshot using the GUI."""
        # Get filename :
        filename = QFileDialog.getSaveFileName(self, 'Screenshot',
                                               os.path.join(os.getenv('HOME'),
                                                            'screenshot.jpg'),
                                               "Picture (*.jpg);;;;All files"
                                               " (*.*)")
        if filename:
            file, ext = os.path.splitext(filename)
            p = QPixmap.grabWindow(self.centralwidget.winId())
            p.save(filename + '.jpg')

    def _toggle_settings(self):
        """Toggle method for display / hide the settings panel."""
        self.q_widget.setVisible(not self.q_widget.isVisible())

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
        unit = self._slRules.currentText()

        # Find closest time index :
        t = [0, 0]
        t[0] = round(np.abs(self._time - xlim[0]).argmin())
        t[1] = round(np.abs(self._time - xlim[1]).argmin())

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
        items = ['Wake', 'N1', 'N2', 'N3', 'REM', 'Art']
        txt = self._slTxtFormat.format(start=str(xlim[0]), end=str(xlim[1]),
                                       unit=unit, conv=items[hypref])
        self._SlText.setText(txt)
        self._SlText.setFont(self._font)

        # ================= HYPNO LABELS =================
        ref = ['Art', 'Wake', 'N1', 'N2', 'N3', 'REM']
        for k, i in zip(self._hypYLabels, ref):
            k.setStyleSheet("QLabel")
        self._hypYLabels[hypref + 1].setStyleSheet("QLabel {color: " +
                                                   self._indicol + ";}")

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
        self._SlVal.setMaximum((self._time.max() - win)/step)
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
            self._chan.set_grid(self._time, step)
        else:
            self._slOnStart = True


    def _fcn_sliderWinSelection(self):
        """Move slider using window spin."""
        self._SlVal.setValue(self._SlGoto.value() / self._SigSlStep.value())

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
        unit = self._slRules.currentText()
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
