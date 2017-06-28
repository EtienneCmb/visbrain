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
        self._brainPickHemi.currentIndexChanged.connect(self._brain_control)

        # Brain template to use :
        self._brainTemplate.setCurrentIndex(int(self.atlas.template[-1]) - 1)
        self._brainTemplate.currentIndexChanged.connect(self._brain_control)

        # Structure :
        self._brainTransp.clicked.connect(self._light_reflection)

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
                self._brainTemplate.setCurrentIndex(int(template[-1]) - 1)
        else:
            self.atlas.template = str(self._brainTemplate.currentText())
            self._cleanProj()

        # Show / hide MNI :
        self.menuDispBrain.setChecked(show)
        self.atlas.mesh.visible = self.menuDispBrain.isChecked()

        # Hemisphere :
        if hemisphere is not None:
            if hemisphere not in ['both', 'left', 'right']:
                raise ValueError("The hemisphere parameter must be either "
                                 "'both', 'left' or 'right'")
            else:
                if hemisphere is 'both':
                    self._brainPickHemi.setCurrentIndex(0)
                elif hemisphere is 'left':
                    self._brainPickHemi.setCurrentIndex(1)
                elif hemisphere is 'rigth':
                    self._brainPickHemi.setCurrentIndex(2)
                self.atlas.reload(hemisphere=hemisphere)
        else:
            currentHemi = int(self._brainPickHemi.currentIndex())
            if currentHemi == 0:
                self.atlas.reload(hemisphere='both')
            elif currentHemi == 1:
                self.atlas.reload(hemisphere='left')
            elif currentHemi == 2:
                self.atlas.reload(hemisphere='right')
            self._cleanProj()

        # Update transformation :
        self._vbNode.transform = self.atlas.transform

    def _light_reflection(self):
        """Change how light is reflected onto the brain.

        The 'internal' option can be used to observe deep structures with a
        fully transparent brain. The 'external' option is only usefull for
        the cortical surface.
        """
        viz = self._brainTransp.isChecked()
        if viz:
            self.atlas.mesh.projection('internal')
        else:
            self.atlas.mesh.projection('external')
            self.atlas.mesh.set_alpha(1.)
        self.o_Brain.setChecked(viz)
        self.o_Brain.setEnabled(viz)
        self.atlas.mesh.update()
