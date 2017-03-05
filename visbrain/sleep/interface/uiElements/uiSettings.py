"""Main class for settings managment."""
import numpy as np

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
        save = QAction("Save", self)
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
        self._SigWin.valueChanged.connect(self._fcn_sliderSettings)
        self._SigWin.setKeyboardTracking(False)
        self._SigSlStep.valueChanged.connect(self._fcn_sliderSettings)
        self._SigSlStep.setKeyboardTracking(False)

    # =====================================================================
    # MENU & FILE MANAGMENT
    # =====================================================================
    def saveFile(self):
        """
        """
        raise ValueError("NOT CONFIGURED")
        # filename = QFileDialog.getSaveFileName(self, 'Save File',
        #                                        os.getenv('HOME'))
        # f = open(filename, 'w')
        # filedata = self.text.toPlainText()
        # f.write(filedata)
        # f.close()

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
        """Screenshot using the GUI.

        This function need that a savename is already defined (otherwise, a
        window appeared so that the user specify the path/name). Then, it needs
        an extension (png) and a boolean parameter (self.cb['export']) to
        specify if the colorbar has to be exported.
        """
        pass

    def _toggle_settings(self):
        """Toggle method for display / hide the settings panel."""
        self.q_widget.setVisible(not self.q_widget.isVisible())

    # =====================================================================
    # SLIDER
    # =====================================================================
    def _fcn_sliderMove(self):
        """Function applied when the slider move."""
        # ---------------------------------------
        # Get slider variables :
        val = self._SlVal.value()
        step = self._SigSlStep.value()
        win = self._SigWin.value()
        xlim = (val*step, val*step+win)
        # ---------------------------------------
        # Find closest time index :
        t = [0, 0]
        t[0] = round(np.abs(self._time - xlim[0]).argmin())
        t[1] = round(np.abs(self._time - xlim[1]).argmin())
        # ---------------------------------------
        # Update display signal :
        sl = slice(t[0], t[1])
        self._chan.set_data(self._sf, self._data, self._time, sl=sl)
        # ---------------------------------------
        # Update spectrogram indicator :
        if self._PanSpecIndic.isChecked():
            ylim = (self._PanSpecFstart.value(), self._PanSpecFend.value())
            self._specInd.set_data(xlim=xlim, ylim=ylim)

        # ---------------------------------------
        # Update hypnogram indicator :
        if self._PanHypIndic.isChecked():
            ylim = (-1, 6)
            self._hypInd.set_data(xlim=xlim, ylim=ylim)

        if self._PanTimeIndic.isChecked():
            self._TimeAxis.set_data(xlim[0], win)

    def _fcn_sliderSettings(self):
        """Function applied to change slider settings."""
        # Set minimum :
        self._SlVal.setMinimum(self._time.min())
        # Set maximum :
        step = self._SigSlStep.value()
        self._SlVal.setMaximum((self._time.max()-self._SigWin.value())/step)
        self._SlVal.setTickInterval(step)
        self._SlVal.setSingleStep(step)

        if self._slOnStart:
            self._fcn_sliderMove()
        else:
            self._slOnStart = True
