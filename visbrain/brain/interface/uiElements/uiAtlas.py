"""Top level class for managing the MNI (rotation, structure...).

Make the bridge between GUI and deep functions. Add some usefull
commands for the user
"""

__all__ = ['uiAtlas']


class uiAtlas(object):
    """Link graphical interface with atlas functions.

    This class can be used to control the part of displayed brain (both / left
    / right hemisphere), the scene rotation and the light behavior.
    """

    def __init__(self):
        """Init."""
        # Brain control :
        self.show_MNI.clicked.connect(self._toggle_brain_visible)
        self.Both_only.clicked.connect(self._brain_control)
        self.Lhemi_only.clicked.connect(self._brain_control)
        self.Rhemi_only.clicked.connect(self._brain_control)

        # Brain template to use :
        self.uiSwitchTemplate.setCurrentIndex(int(self.atlas.template[-1]) - 1)
        self.uiSwitchTemplate.currentIndexChanged.connect(self._brain_control)

        # Structure :
        eval('self.q_' + self.atlas.projection + '.setChecked(True)')
        self.q_internal.clicked.connect(self._light_reflection)
        self.q_external.clicked.connect(self._light_reflection)

        self.struct_color_edit.setPlaceholderText("'red', #ab4642, (1,0,0)...")

    def _brain_control(self, _, template=None, show=True, hemisphere=None):
        """Control the type of brain to use.

        Kargs:
            template: string, optional, (def: None)
                Template to use for the MNI brain. Use either 'B1', 'B2' or
                'B3'.

            show: bool, optional, (def: True)
                Show (True) or hide (False) the MNI brain.

            hemisphere: string, optional, (def: None)
                Define if you want to see only 'left' or 'right'hemisphere.
                Otherwise use 'both'.
        """
        # Template :
        if template is not None:
            if template not in ['B1', 'B2', 'B3']:
                raise ValueError("The template parameter must be either 'B1', "
                                 "'B2 or 'B3'")
            else:
                self.uiSwitchTemplate.setCurrentIndex(int(template[-1]) - 1)
        else:
            self.atlas.template = str(self.uiSwitchTemplate.currentText())

        # Show / hide MNI :
        self.show_MNI.setChecked(show)
        self.atlas.mesh.visible = self.show_MNI.isChecked()

        # Hemisphere :
        if hemisphere is not None:
            if hemisphere not in ['both', 'left', 'right']:
                raise ValueError("The hemisphere parameter must be either "
                                 "'both', 'left' or 'right'")
            else:
                order = (['both', 'left', 'right'],
                         ['Both_only', 'Lhemi_only', 'Rhemi_only'])
                self.atlas.reload(hemisphere=hemisphere)
                eval('self.' + order[1][order[0].index(
                                    hemisphere)] + '.setChecked(True)')
        else:
            if self.Both_only.isChecked():
                self.atlas.reload(hemisphere='both')
            elif self.Lhemi_only.isChecked():
                self.atlas.reload(hemisphere='left')
            elif self.Rhemi_only.isChecked():
                self.atlas.reload(hemisphere='right')

        # Update transformation :
        self._vbNode.transform = self.atlas.transform
        self.view.wc.camera.set_range(x=self._xRange, y=self._yRange,
                                      z=self._zRange)

    def _light_reflection(self):
        """Change how light is reflected onto the brain.

        The 'internal' option can be used to observe deep structures with a
        fully transparent brain. The 'external' option is only usefull for
        the cortical surface.
        """
        if self.q_internal.isChecked():
            self.atlas.mesh.projection('internal')
        elif self.q_external.isChecked():
            self.atlas.mesh.projection('external')
        self.atlas.mesh.update()

    def _toggle_brain_visible(self):
        """Toggle to display / hide the brain."""
        viz = not self.atlas.mesh.visible
        self.atlas.mesh.visible = viz
        self.show_MNI.setChecked(viz)
        self.toolBox_2.setEnabled(viz)
