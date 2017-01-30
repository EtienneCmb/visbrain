"""Main class for settings managment (save / load / light / cameras...).


"""

import os
from PyQt4.QtGui import *


from vispy import io
import vispy.scene.cameras as viscam

from ...utils import uiSpinValue

__all__ = ['uiSettings']


class uiSettings(object):
    """Main class for settings managment (save / load / light / cameras...)."""

    def __init__(self):
        """Init."""
        # ***********************************************************
        # MENU
        # ***********************************************************
        self.progressBar.hide()

        # --------------- FILE ---------------
        # Screenshot :
        screenshot = QAction("Screenshot", self)
        screenshot.setShortcut("Ctrl+N")
        screenshot.triggered.connect(self.screenshot)
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

        # Transform :
        self.actionProjection.triggered.connect(self.cortical_projection)
        self.actionRepartition.triggered.connect(self.cortical_repartition)

        # ***********************************************************
        # SETTINGS PANEL
        # ***********************************************************
        # Quick settings panel :
        self.actionQuick_settings.triggered.connect(
            self.show_hide_quick_settings)

        # Background color :
        self.bgd_green.valueChanged.connect(self.fcn_bgd_color)
        self.bgd_red.valueChanged.connect(self.fcn_bgd_color)
        self.bgd_blue.valueChanged.connect(self.fcn_bgd_color)

        # ***********************************************************
        # LIGHT
        # ***********************************************************
        # Position :
        self.uil_posX.valueChanged.connect(self.uiSet_light)
        self.uil_posY.valueChanged.connect(self.uiSet_light)
        self.uil_posZ.valueChanged.connect(self.uiSet_light)
        # Intensity :
        self.uil_intX.valueChanged.connect(self.uiSet_light)
        self.uil_intY.valueChanged.connect(self.uiSet_light)
        self.uil_intZ.valueChanged.connect(self.uiSet_light)
        # Color :
        self.uil_colR.valueChanged.connect(self.uiSet_light)
        self.uil_colG.valueChanged.connect(self.uiSet_light)
        self.uil_colB.valueChanged.connect(self.uiSet_light)
        self.uil_colA.valueChanged.connect(self.uiSet_light)
        # Coeffient :
        self.uil_AmbCoef.valueChanged.connect(self.uiSet_light)
        self.uil_SpecCoef.valueChanged.connect(self.uiSet_light)

        self.uiUpdate_light()

        # ***********************************************************
        # CAMERAS
        # ***********************************************************
        # Cameras types :
        self.c_Turnable.clicked.connect(self._fcn_switch_camera)
        self.c_Fly.clicked.connect(self._fcn_switch_camera)

    def screenshot(self):
        """
        """
        # Manage filename :
        if self._savename == None:
            self._savename = QFileDialog.getSaveFileName(
                self, 'Save screenshot', os.getenv('HOME'))
        if self._savename.find('.'+self._extension) == -1:
            self._savename += '.'+self._extension

        # Manage size exportation :
        backp_size = self.view.canvas.physical_size
        ratio = max(6000/backp_size[0], 3000/backp_size[1])
        new_size = (int(backp_size[0]*ratio), int(backp_size[1]*ratio))
        self.view.canvas._backend._physical_size = new_size

        # Render and save :
        img = self.view.canvas.render(region=self._crop)
        io.imsave(self._savename, img, format=self._extension)

        if self.cb['export']:
            cbimg = self.view.cbcanvas.render()
            if self._savename.find('.')+1:
                filename = self._savename.replace('.', '_colorbar.')
            else:
                filename += '_colorbar'
            io.imsave(filename, cbimg, format=self._extension)
        self.view.canvas._backend._physical_size = backp_size
        self.view.canvas.update()
        self.atlas.mesh.update()

    def saveFile(self):
        """
        """
        filename = QFileDialog.getSaveFileName(
            self, 'Save File', os.getenv('HOME'))
        # f = open(filename, 'w')
        # filedata = self.text.toPlainText()
        # f.write(filedata)
        # f.close()

    def openFile(self):
        """
        """
        filename = QFileDialog.getSaveFileName(
            self, 'Open File', os.getenv('HOME'))
        # f = open(filename, 'w')
        # filedata = self.text.toPlainText()
        # f.write(filedata)
        # f.close()

    def show_hide_quick_settings(self):
        """
        """
        self.q_widget.setVisible(not self.q_widget.isVisible())

    def fcn_bgd_color(self):
        """Change canvas background color
        """
        bgd = (self.bgd_red.value(), self.bgd_green.value(),
               self.bgd_blue.value())
        self.view.canvas.bgcolor = bgd

    def uiSet_light(self):
        """
        """
        # Position :
        l_pos = (self.uil_posX.value(), self.uil_posY.value(),
                 self.uil_posZ.value())
        # Intensity :
        l_int = (self.uil_intX.value(), self.uil_intY.value(),
                 self.uil_intZ.value())
        # Color :
        l_col = (self.uil_colR.value(), self.uil_colG.value(),
                 self.uil_colB.value(), self.uil_colA.value())
        # Coef :
        l_amb, l_spec = self.uil_AmbCoef.value(), self.uil_SpecCoef.value()

        self.atlas.mesh.set_light(l_position=l_pos, l_color=l_col,
                                  l_intensity=l_int, l_coefAmbient=l_amb,
                                  l_coefSpecular=l_spec)

    def uiUpdate_light(self):
        """
        """
        uiSpinValue([self.uil_posX, self.uil_posY, self.uil_posZ,
                     self.uil_intX, self.uil_intY, self.uil_intZ,
                     self.uil_colR, self.uil_colG, self.uil_colB,
                     self.uil_colA, self.uil_AmbCoef, self.uil_SpecCoef],
                    self.atlas.mesh.get_light)

    def _fcn_switch_camera(self):
        """Switch between different types of cameras.

        The user can either use a Turntable or a Fly camera. The turntable
        camera is centered on the central object. Every rotation is arround
        this object. The fly camera can be used for go in every deep part of
        the brain (not easy to control).
        """
        # Get radio buttons values :
        if self.c_Turnable.isChecked():
            camera = viscam.TurntableCamera(distance=10.0, fov=10, azimuth=0)
        if self.c_Fly.isChecked():
            # camera = viscam.PanZoomCamera(aspect=1)
            camera = viscam.FlyCamera()

        # Add camera to the mesh and to the canvas :
        self.view.wc.camera = camera
        self.atlas.mesh.set_camera(camera)
        self.view.wc.update()