"""Main class for settings managment."""

import os
from PyQt4.QtGui import *
from vispy import io


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
        # Ui settings panel :
        if self.actionUi_settings.isChecked():
            self.QuickSettings.setCurrentIndex(0)
            self.q_widget.setVisible(True)
            self.actionUi_settings.setChecked(False)
        # Nd-Plot panel :
        elif self.actionNdPlt.isChecked():
            self.QuickSettings.setCurrentIndex(1)
            self.q_widget.setVisible(True)
            self.actionNdPlt.setChecked(False)
        # 1d-plot panel :
        elif self.actionOnedPlt.isChecked():
            self.QuickSettings.setCurrentIndex(2)
            self.q_widget.setVisible(True)
            self.actionOnedPlt.setChecked(False)
        # Image panel :
        elif self.actionImage.isChecked():
            self.QuickSettings.setCurrentIndex(3)
            self.q_widget.setVisible(True)
            self.actionImage.setChecked(False)
        # Colormap panel :
        elif self.actionColormap.isChecked():
            self.QuickSettings.setCurrentIndex(4)
            self.q_widget.setVisible(True)
            self.actionColormap.setChecked(False)

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
