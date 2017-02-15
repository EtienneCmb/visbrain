"""Main class for settings managment."""

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

        # ------------------------------- MENU -------------------------------
        self.actionUi_settings.triggered.connect(self._fcn_panSettingsViz)
        self.actionNdPlt.triggered.connect(self._fcn_panSettingsViz)
        self.actionOnedPlt.triggered.connect(self._fcn_panSettingsViz)
        self.actionImage.triggered.connect(self._fcn_panSettingsViz)
        self.actionColormap.triggered.connect(self._fcn_panSettingsViz)

        # ------------------------------ CANVAS ------------------------------
        # Set canvas visibility control :
        self._CanVisNd.clicked.connect(self._fcn_CanVisToggle)
        self._CanVis1d.clicked.connect(self._fcn_CanVisToggle)
        # self._CanVisImage.clicked.connect(self._fcn_CanVisToggle)
        self._CanVisNd.setChecked(True)

        # ------------------------------ TABS ------------------------------
        self.QuickSettings.currentChanged.connect(self._fcn_tabSelection)

        # =====================================================================
        # SETTINGS PANEL
        # =====================================================================
        # Quick settings panel :
        self.actionQuick_settings.triggered.connect(self._toggle_settings)

        # Background color :
        self._uiBgdRed.valueChanged.connect(self._fcn_bgd_color)
        self._uiBgdGreen.valueChanged.connect(self._fcn_bgd_color)
        self._uiBgdBlue.valueChanged.connect(self._fcn_bgd_color)

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

    def _fcn_tabSelection(self):
        if self.QuickSettings.currentIndex() == 1:
            self._fcn_ndAxis_update()
        if self.QuickSettings.currentIndex() == 2:
            self._fcn_1dAxis_update()
        elif self.QuickSettings.currentIndex() == 3:
            self._fcn_imAxis_update()
        pass

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
        # Manage filename :
        if self._savename is None:
            self._savename = QFileDialog.getSaveFileName(
                self, 'Save screenshot', os.getenv('HOME'))
        if self._savename.find('.' + self._extension) == -1:
            self._savename += '.' + self._extension
        else:
            raise ValueError("No extension detected.")

        # Manage size exportation. The dpi option present when creating a
        # vispy canvas doesn't seems to work. The trick bellow increase the
        # physical size of the canvas so that the exported figure has a
        # high-definition :
        # Get a copy of the actual canvas physical size :
        backp_size = self.view.canvas.physical_size
        # Increase the physical size :
        ratio = max(6000/backp_size[0], 3000/backp_size[1])
        new_size = (int(backp_size[0]*ratio), int(backp_size[1]*ratio))
        self.view.canvas._backend._physical_size = new_size

        # Render and save :
        img = self.view.canvas.render(region=self._crop)
        io.imsave(self._savename, img, format=self._extension)

        # Export the colorbar :
        if self.cb['export']:
            # Render colorbar panel :
            cbimg = self.view.cbcanvas.render()
            # Colorbar file name : filename_colorbar.extension
            if self._savename.find('.') + 1:
                filename = self._savename.replace('.', '_colorbar.')
            else:
                filename += '_colorbar'
            io.imsave(filename, cbimg, format=self._extension)
        # Set to the canvas it's previous size :
        self.view.canvas._backend._physical_size = backp_size
        # Update the canvas :
        self.view.canvas.update()
        self.atlas.mesh.update()

    def _toggle_settings(self):
        """Toggle method for display / hide the settings panel."""
        self.q_widget.setVisible(not self.q_widget.isVisible())

    def _fcn_bgd_color(self):
        """Change canvas background color."""
        bgd = (self._uiBgdRed.value(), self._uiBgdGreen.value(),
               self._uiBgdBlue.value())
        self.view.canvas.bgcolor = bgd
