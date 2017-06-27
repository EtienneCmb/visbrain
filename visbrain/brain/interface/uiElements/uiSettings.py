# -*- coding: utf-8 -*-

"""Main class for settings managment (save / load / light / cameras...)."""
import os
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtWidgets

import vispy.scene.cameras as viscam

from ....utils import uiSpinValue
from ....io import write_fig_canvas

__all__ = ['uiSettings']


class uiSettings(object):
    """Main class for settings managment (save / load / light / cameras...)."""

    def __init__(self):
        """Init."""
        # =============================================================
        # MENU & FILES
        # =============================================================
        self.progressBar.hide()

        # ------------- Screenshot / Exit -------------
        self.actionScreenshot.triggered.connect(self._screenshot)
        self.actionExit.triggered.connect(QtWidgets.qApp.quit)

        # ------------- Transform -------------
        self.actionProjection.triggered.connect(self._fcn_menuProjection)
        self.actionRepartition.triggered.connect(self._fcn_menuRepartition)

        # ------------- Help -------------
        self.actionShortcut.triggered.connect(self._fcn_showShortPopup)
        self.actionDocumentation.triggered.connect(self._fcn_openDoc)

        # =============================================================
        # SCREENSHOT
        # =============================================================
        # Set values :
        self._ssResolution.setValue(self._uirez)
        self._ssSaveAs.setPlaceholderText("myfile")
        if self._crop is not None:
            self._ssCropXs.setValue(self._crop[0])
            self._ssCropYs.setValue(self._crop[1])
            self._ssCropXe.setValue(self._crop[2])
            self._ssCropYe.setValue(self._crop[2])
        # Connections :
        self._ssSaveAs.editingFinished.connect(self._screenshotSettings)
        self._ssSaveAsExt.currentIndexChanged.connect(self._screenshotSettings)
        self._ssCropEnable.clicked.connect(self._screenshotSettings)
        self._ssResolution.valueChanged.connect(self._screenshotSettings)
        self._ssCbEnable.clicked.connect(self._screenshotSettings)
        self._ssRun.clicked.connect(self._fcn_runScreenshot)
        self._ssAutoCrop.clicked.connect(self._screenshotSettings)
        self._ssCropXs.valueChanged.connect(self._screenshotSettings)
        self._ssCropYs.valueChanged.connect(self._screenshotSettings)
        self._ssCropXe.valueChanged.connect(self._screenshotSettings)
        self._ssCropYe.valueChanged.connect(self._screenshotSettings)

        # Background color :
        self.bgd_green.valueChanged.connect(self._fcn_bgd_color)
        self.bgd_red.valueChanged.connect(self._fcn_bgd_color)
        self.bgd_blue.valueChanged.connect(self._fcn_bgd_color)

        # =============================================================
        # LIGHT
        # =============================================================
        # Position :
        self.uil_posX.valueChanged.connect(self._light_Ui2Atlas)
        self.uil_posY.valueChanged.connect(self._light_Ui2Atlas)
        self.uil_posZ.valueChanged.connect(self._light_Ui2Atlas)
        # Intensity :
        self.uil_intX.valueChanged.connect(self._light_Ui2Atlas)
        self.uil_intY.valueChanged.connect(self._light_Ui2Atlas)
        self.uil_intZ.valueChanged.connect(self._light_Ui2Atlas)
        # Color :
        self.uil_colR.valueChanged.connect(self._light_Ui2Atlas)
        self.uil_colG.valueChanged.connect(self._light_Ui2Atlas)
        self.uil_colB.valueChanged.connect(self._light_Ui2Atlas)
        self.uil_colA.valueChanged.connect(self._light_Ui2Atlas)
        # Coeffient :
        self.uil_AmbCoef.valueChanged.connect(self._light_Ui2Atlas)
        self.uil_SpecCoef.valueChanged.connect(self._light_Ui2Atlas)

        self._light_Atlas2Ui()

        # =============================================================
        # ERROR // WARNING MESSAGES
        # =============================================================
        # Hide Error / warning wessage :
        self.UserMsgBox.setVisible(False)
        # Hide rotation panel :
        self.userRotationPanel.setVisible(False)

    # =============================================================
    # MENU & FILE MANAGMENT
    # =============================================================
    def _fcn_showShortPopup(self):
        """Open shortcut window."""
        self._shpopup.show()

    def _fcn_openDoc(self):
        """Open documentation."""
        import webbrowser
        webbrowser.open('http://etiennecmb.github.io/visbrain/brain.html')

    # =============================================================
    # SCREENSHOT
    # =============================================================
    def _fcn_runScreenshot(self):
        """Run the screenshot."""
        # Get latest settings :
        self._screenshotSettings()
        # Run screenshot :
        self._screenshot()

    def _screenshotSettings(self):
        """Get screenshot settings from the GUI.s"""
        # ------------- MAIN CANVAS -------------
        # Get filename :
        file = str(self._ssSaveAs.text())
        ext = str(self._ssSaveAsExt.currentText())
        self._savename = file + ext
        # Cropping :
        self._autocrop = self._ssAutoCrop.isChecked()
        self._ssCropEnable.setEnabled(not self._autocrop)

        viz = self._ssCropEnable.isChecked()
        crop = (self._ssCropXs.value(), self._ssCropYs.value(),
                self._ssCropXe.value(), self._ssCropYe.value())
        self._crop = crop if viz else None
        self._ssCropW.setEnabled((not self._autocrop) and viz)
        # Resolution :
        self._uirez = float(self._ssResolution.value())

        # ------------- COLORBAR CANVAS -------------
        # Colorbar :
        viz = self._ssCbEnable.isChecked()
        self.menuDispCbar.setChecked(viz)
        self._fcn_menuCbar()
        self.cb['export'] = viz

    def _screenshot(self):
        """Screenshot using the GUI.

        This function need that a savename is already defined (otherwise, a
        window appeared so that the user specify the path/name). Then, it needs
        an extension (png) and a boolean parameter (self.cb['export']) to
        specify if the colorbar has to be exported.
        """
        # Manage filename :
        if isinstance(self._savename, str):
            cond = self._savename.split('.')[0] == ''
        if (self._savename is None) or cond:
            saveas = str(QFileDialog.getSaveFileName(self, 'Save screenshot',
                                                     os.getenv('HOME')))
        else:
            saveas = self._savename

        # Get filename and extension :
        file, ext = os.path.splitext(saveas)
        if not ext:
            raise ValueError("No extension detected in "+saveas)

        # Export the main canvas :
        write_fig_canvas(saveas, self.view.canvas, resolution=self._uirez,
                         autocrop=self._autocrop, region=self._crop)

        # Export the colorbar :
        # self.cb['export'] = True
        if self.cb['export']:
            # Colorbar file name : filename_colorbar.extension
            saveas = saveas.replace('.', '_colorbar.')

            # Export the colorbar canvas :
            write_fig_canvas(saveas, self.view.cbcanvas, region=self._cbcrop,
                             autocrop=self._autocrop, resolution=self._uirez)

    def _fcn_bgd_color(self):
        """Change canvas background color."""
        bgd = (self.bgd_red.value(), self.bgd_green.value(),
               self.bgd_blue.value())
        self.view.canvas.bgcolor = bgd
        self.view.cbcanvas.bgcolor = bgd

    def _fcn_menuProjection(self):
        """Run the cortical projection."""
        self._tprojectas = 'activity'
        self._sourcesProjection()

    def _fcn_menuRepartition(self):
        """Run the cortical projection."""
        self._tprojectas = 'repartition'
        self._sourcesProjection()

    # =============================================================
    # ROTATION
    # =============================================================
    def _rotate(self, fixed=None, custom=None):
        """Rotate the scene elements using a predefined or a custom rotation.

        The rotation is applied on every objects on the scene.

        Kargs:
            fixed: string, optional, (def: 'axial')
                Predefined rotation. Use either 'axial', 'coronal' or
                'sagittal'. As a complement, use the suffixe '_0' or
                '_1' to switch between possible views.
                    * 'axial_0/1': switch between top/bottom view
                    * 'coronal_0/1': switch between front/back view
                    * 'sagittal_0/1': switch between left/right view

            custom: tuple, optional, (def: None)
                Custom rotation. The custom parameter must be a
                tuple of two float respectively for azimuth and
                elevation.
        """
        # Check the fixed parameter :
        if fixed is not None:
            if not isinstance(fixed, str) or not any([bool(fixed.find(
                            k)+1) for k in ['axial', 'sagittal', 'coronal']]):
                raise ValueError("fixed must contain 'axial', 'coronal' or "
                                 "'sagittal")
            else:
                if bool(fixed.find('_')+1):
                    view, side = tuple(fixed.split('_'))
                    exec('self.atlas.' + view + ' = ' + side)
                else:
                    view, side = fixed, None
        else:
            view, side = None, None
        # Check the custom parameter :
        if custom is not None:
            if not isinstance(custom, (tuple, list)) or len(custom) is not 2:
                raise ValueError("The custom parameter must be a tuple of "
                                 "two floats (azimuth, elevation)")

        azimuth, elevation = 0, 90
        if view is not None:
            # Sagittal (left, right)
            if view == 'sagittal':
                if self.atlas.sagittal == 0:  # Left
                    azimuth, elevation = -90, 0
                    self.atlas.sagittal = 1
                elif self.atlas.sagittal == 1:  # Right
                    azimuth, elevation = 90, 0
                    self.atlas.sagittal = 0
                self.atlas.coronal, self.atlas.axial = 0, 0
            # Coronal (front, back)
            elif view == 'coronal':
                if self.atlas.coronal == 0:  # Front
                    azimuth, elevation = 180, 0
                    self.atlas.coronal = 1
                elif self.atlas.coronal == 1:  # Back
                    azimuth, elevation = 0, 0
                    self.atlas.coronal = 0
                self.atlas.sagittal, self.atlas.axial = 0, 0
            # Axial (top, bottom)
            elif view == 'axial':
                if self.atlas.axial == 0:  # Top
                    azimuth, elevation = 0, 90
                    self.atlas.axial = 1
                elif self.atlas.axial == 1:  # Bottom
                    azimuth, elevation = 0, -90
                    self.atlas.axial = 0
                self.atlas.sagittal, self.atlas.coronal = 0, 0
        elif custom is not None:
            azimuth, elevation = custom[0], custom[1]

        # Set camera and range :
        self.view.wc.camera.azimuth = azimuth
        self.view.wc.camera.elevation = elevation
        self._set_cam_range()

    def _set_cam_range(self, name='turntable'):
        """Set the camera range."""
        dic = self._xyzRange[name]
        self.view.wc.camera.set_range(x=dic['x'], y=dic['x'], z=dic['z'])

    # =============================================================
    # LIGHT
    # =============================================================
    def _light_Ui2Atlas(self):
        """Get light properties from the GUI and set it to the atlas.

        This function get light position / Intensity / Color / Coefficients
        from the graphical user interface and set it to the atlas.
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

    def _light_Atlas2Ui(self):
        """Get light properties from the atlas and set it to the GUI.

        This function get light position / Intensity / Color / Coefficients
        from the atlas and set it to the graphical user interface.
        """
        uiSpinValue([self.uil_posX, self.uil_posY, self.uil_posZ,
                     self.uil_intX, self.uil_intY, self.uil_intZ,
                     self.uil_colR, self.uil_colG, self.uil_colB,
                     self.uil_colA, self.uil_AmbCoef, self.uil_SpecCoef],
                    self.atlas.mesh.get_light)

    # =============================================================
    # ERROR // WARNING MESSAGES
    # =============================================================
    def _userMsg(self, message, kind='error', during=10, fontsize=9):
        """Display error / warning message to the user.

        This method display an error / warning message for the user. This
        message is displayed at the bottom of the settings panel.

        Args:
            message: str
                The message to displayed.

        Kargs:
            kind: str, optional, (def: 'error')
                The type of message to display. Use either 'error' (for a red
                bold error message) or 'warn' (for a blue message.)

            during: float, optional, (def: 10.0)
                The duration of the message. After this delay, the message
                disapear.

            fontsize: int, optional, (def: 9)
                The fontsize of the displayed message.
        """
        # Only display this message if there's no already present message :
        if not self.UserMsgBox.isVisible():
            # Set settings panel visible :
            self.q_widget.setVisible(True)

            # Set the widget and the error message visible :
            self.UserMsgBox.setVisible(True)
            self.uiErrorMsg.setVisible(True)

            # Change the color depending on warning / error type :
            palette = QPalette()
            palette.setColor(QPalette.Background, QtCore.Qt.white)
            # Error type :
            if kind is 'error':
                message = 'ERROR:\n' + message
                palette.setColor(QPalette.Foreground, QtCore.Qt.red)
            # Warning type :
            elif kind is 'warn':
                message = 'Warning:\n' + message
                palette.setColor(QPalette.Foreground, QtCore.Qt.blue)
            else:
                raise ValueError("Choose either between 'error' or 'warn'.")

            # Set message text and color:
            self.uiErrorMsg.setText(message)
            self.uiErrorMsg.setAutoFillBackground(True)
            self.uiErrorMsg.setPalette(palette)
            self.uiErrorMsg.setFont(QFont("Times", fontsize, QFont.Bold))

            # Message disappear :
            def _delayedMsg():
                self.UserMsgBox.setVisible(False)
                self.uiErrorMsg.setVisible(False)

            # Set a pyqt timer to delayed when the message is hide :
            timer = QtCore.QTimer()
            timer.singleShot(during * 1000, _delayedMsg)

    def _fcn_userRotation(self):
        """Display rotation informations.

        This function display rotation informations (azimuth / elevation /
        distance) at the bottom of the setting panel.
        """
        # Define and set the rotation string :
        rotstr = 'Azimuth: {az}°, Elevation: {el}°, Distance: {di}'
        # Get camera Azimuth / Elevation / Distance :
        az = str(self.view.wc.camera.azimuth)
        el = str(self.view.wc.camera.elevation)
        di = str(round(self.view.wc.camera.distance * 100) / 100)
        # Set the text to the box :
        self.userRotation.setText(rotstr.format(az=az, el=el, di=di))
