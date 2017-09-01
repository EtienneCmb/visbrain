# -*- coding: utf-8 -*-

"""Main class for settings managment (save / load / light / cameras...)."""
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtGui import QPalette, QFont

from ....utils import set_spin_values

__all__ = ['uiSettings']


class uiSettings(object):
    """Main class for settings managment (save / load / light / cameras...)."""

    def __init__(self):
        """Init."""
        self.progressBar.hide()

        # =============================================================
        # GUI
        # =============================================================
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
    def _fcn_tab_changed(self):
        """Executed function when the user change the tab."""
        # Get tab name :
        tabname = str(self.QuickSettings.currentWidget().objectName())
        # 
        if (tabname == 'q_CONNECT') and (self.connect.name != 'NoneConnect'):
            self.cbqt.select('Connectivity')
        elif (tabname == 'q_SOURCES') and (self.sources.name != 'NoneSources'):
            if self._modproj is not None:
                self.cbqt.select('Projection')

    # =============================================================
    # GUI
    # =============================================================
    def _fcn_bgd_color(self):
        """Change canvas background color."""
        bgd = (self.bgd_red.value(), self.bgd_green.value(),
               self.bgd_blue.value())
        self.view.canvas.bgcolor = bgd

    # =============================================================
    # ROTATION
    # =============================================================
    def _rotate(self, fixed=None, custom=None, margin=0.08):
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
                scale_factor = 2 * self.atlas.mesh._camratio[0]
            # Coronal (front, back)
            elif view == 'coronal':
                if self.atlas.coronal == 0:  # Front
                    azimuth, elevation = 180, 0
                    self.atlas.coronal = 1
                elif self.atlas.coronal == 1:  # Back
                    azimuth, elevation = 0, 0
                    self.atlas.coronal = 0
                self.atlas.sagittal, self.atlas.axial = 0, 0
                scale_factor = 2 * self.atlas.mesh._camratio[1]
            # Axial (top, bottom)
            elif view == 'axial':
                if self.atlas.axial == 0:  # Top
                    azimuth, elevation = 0, 90
                    self.atlas.axial = 1
                elif self.atlas.axial == 1:  # Bottom
                    azimuth, elevation = 0, -90
                    self.atlas.axial = 0
                self.atlas.sagittal, self.atlas.coronal = 0, 0
                scale_factor = 2 * self.atlas.mesh._camratio[2]
        elif custom is not None:
            azimuth, elevation = custom[0], custom[1]
            scale_factor = 2 * self.atlas.mesh._camratio[2]

        # Set camera and range :
        self.view.wc.camera.azimuth = azimuth
        self.view.wc.camera.elevation = elevation
        self.view.wc.camera.scale_factor = (1. + margin) * scale_factor

    def _set_cam_range(self, name='turntable'):
        """Set the camera range."""
        dic = self._xyzRange[name]
        self.view.wc.camera.set_range(x=dic['x'], y=dic['y'], z=dic['z'])

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
                                  l_intensity=l_int, l_ambient=l_amb,
                                  l_specular=l_spec)

    def _light_Atlas2Ui(self):
        """Get light properties from the atlas and set it to the GUI.

        This function get light position / Intensity / Color / Coefficients
        from the atlas and set it to the graphical user interface.
        """
        set_spin_values([self.uil_posX, self.uil_posY, self.uil_posZ,
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
        rotstr = 'Azimuth: {a}°, Elevation: {e}°,\nDistance: {d}, Scale: {s}'
        # Get camera Azimuth / Elevation / Distance :
        a = str(self.view.wc.camera.azimuth)
        e = str(self.view.wc.camera.elevation)
        d = str(np.around(self.view.wc.camera.distance, 2))
        s = str(np.around(self.view.wc.camera.scale_factor, 2))
        # Set the text to the box :
        self.userRotation.setText(rotstr.format(a=a, e=e, d=d, s=s))
