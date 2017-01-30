"""This file contains user dedicated functions for a direct interaction.

Those functions are a the top level of a visbrain instance and are defined in
order to run commands without the necessity of opening the interface. This is
really convenient for generating a large number of pictures by looping over a
vbrain instance.
"""

__all__ = ['userfcn']


class userfcn(object):
    """Group all functions accessible by the user.

    Those functions are grouped in the following categories:
        * Settings (load / save / screenshot / rotation...)
        * Brain control (hemisphere / light...)
        * Sources (cortical projection / repartition...)
        * Connectivity
        * Sub-structures
    """

    ###########################################################################
    ###########################################################################
    #                             SETTINGS
    ###########################################################################
    ###########################################################################
    def rotate(self, fixed=None, custom=None):
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

        Example:
            >>> # Define a vbrain instance :
            >>> vb = vbrain()
            >>> # Predefined rotation :
            >>> vb.rotate(fixed='sagittal_1')
            >>> # Custom rotation :
            >>> vb.rotate(custom=(90.0, 0.0))
            >>> # Show the GUI :
            >>> vb.show()
        """
        self._rotate(fixed=fixed, custom=custom)

    def background_color(self, color=(.1, .1, .1)):
        """
        """
        pass

    def screenshot(self, name, crop=None):
        """
        """
        pass

    ###########################################################################
    ###########################################################################
    #                           BRAIN CONTROL
    ###########################################################################
    ###########################################################################
    def brain_control(self, template=None, show=True, hemisphere=None):
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

        Example:
            >>> # Define a vbrain instance :
            >>> vb = vbrain()
            >>> # Display the right hemisphere of 'B3' template :
            >>> vb.brain_control(template='B3', hemisphere='right')
            >>> # Show the GUI :
            >>> vb.show()
        """
        self._brain_control(template=template, show=show,
                            hemisphere=hemisphere)

    def brain_opacity(self, alpha=0.1, show=True):
        """Set the level of transparency of the brain.

        Kargs:
            alpha: float, optional, (def: 0.1)
                Transparency level (usually between 0 and 1).

            show: bool, optional, (def: True)
                Specify if the brain has be shown.

        Example:
            >>> # Define a vbrain instance :
            >>> vb = vbrain()
            >>> # Set transparency :
            >>> vb.brain_opacity(alpha=0.1, show=True)
            >>> # Show the GUI :
            >>> vb.show()
        """
        # Force to have internal projection :
        self.atlas.mesh.projection('internal')
        self.atlas.mesh.visible = show
        self.show_MNI.setChecked(show)
        self.atlas.mesh.set_alpha(alpha)

    def light_reflection(self, reflect_on=None):
        """Change how light is reflected onto the brain.

        This function can be used to see either the surface only (external) or
        deep voxels inside the brain (internal).

        Kargs:
            reflect_on: string, optional, (def: None)
                Choose either between 'internal' or 'external'. Inside the
                graphical interface, this can be done using the shortcut 3.

        Example:
            >>> # Define a vbrain instance :
            >>> vb = vbrain()
            >>> # Display the external surface :
            >>> vb.light_reflection(reflect_on='external')
            >>> # Show the GUI :
            >>> vb.show()
        """
        if reflect_on is not None:
            if reflect_on not in ['internal', 'external']:
                raise ValueError("The reflect_on parameter must be either "
                                 "'internal' or 'external'")
            else:
                eval('self.q_' + reflect_on + '.setChecked(True)')
        self._light_reflection()

    ###########################################################################
    ###########################################################################
    #                              SOURCES
    ###########################################################################
    ###########################################################################
    def sources_opacity(self, alpha=1., show=True):
        """Set the level of transparency of sources.

        Kargs:
            alpha: float, optional, (def: 1.)
                Transparency level (usually between 0 and 1).

            show: bool, optional, (def: True)
                Specify if sources has be shown.

        Example:
            >>> # Define a vbrain instance with 10 random sources:
            >>> vb = vbrain(s_xyz=np.random.randint(-20, 20, (10, 3)))
            >>> # Set transparency :
            >>> vb.sources_opacity(alpha=0.1, show=True)
            >>> # Show the GUI :
            >>> vb.show()
        """
        if alpha >= 0.95:
            self.sources.mesh.set_gl_state('translucent', depth_test=False)
        else:
            self.sources.mesh.set_gl_state('translucent', depth_test=True)
        self.sources.sColor[:, 3] = alpha
        self.sources.edgecolor[:, 3] = alpha
        self.sources.update()
        self.sources.mesh.visible = show

    ###########################################################################
    ###########################################################################
    #                            CONNECTIVITY
    ###########################################################################
    ###########################################################################

    ###########################################################################
    ###########################################################################
    #                           SUB-STRUCTURES
    ###########################################################################
    ###########################################################################
    def area_plot(self, selection=[], subdivision='brod'):
        """Select some area to plot.

        Kargs:
            selection: list, optional, (def: [])
                List of integers where each one refer to a particular area. The
                corresponding list can be found in the graphical interface in
                the MNI -> Strucures -> Select structures tab.

            subdivision: str, optional, (def: 'brod')
                Select the sub-division method i.e 'brod' (for brodmann areas)
                or 'aal' (Anatomical Automatic Labeling)

        Example:
            >>> # Define a vbrain instance :
            >>> vb = vbrain()
            >>> # Display brodmann area 4 and 6 :
            >>> vb.area_plot(selection=[4, 6], subdivision='brod')
            >>> # Show the GUI :
            >>> vb.show()
        """
        # Inputs checking :
        if not isinstance(selection, list):
            raise ValueError("The selection parameter must be a list of "
                             "integers")
        if subdivision not in ['brod', 'aal']:
            raise ValueError("The subdivision parameter must either be 'brod' "
                             "or 'aal'")

        # Area selection (only if it's not empty) :
        if selection:
            selection.sort()
            self.area.select = selection
            self.area.structure = subdivision

            # Add areas to the plot :
            self._area_plot()

    def area_light_reflection(self, reflect_on=None):
        """Change how light is refleting onto sub-areas.

        This function can be used to see either the surface only (external) or
        deep voxels inside areas (internal).

        Kargs:
            reflect_on: string, optional, (def: None)
                Choose either to reflect on 'internal' or 'external'.

        Example:
            >>> # Define a vbrain instance :
            >>> vb = vbrain()
            >>> # Display brodmann area 4 and 6 :
            >>> vb.area_plot(selection=[4, 6], subdivision='brod')
            >>> # Display the external surface :
            >>> vb._area_light_reflection(reflect_on='internal')
            >>> # Hide the brain :
            >>> vb.brain_opacity(show=False)
            >>> # Show the GUI :
            >>> vb.show()
        """
        if reflect_on is not None:
            if reflect_on not in ['internal', 'external']:
                raise ValueError("The reflect_on parameter must be either "
                                 "'internal' or 'external'")
            else:
                eval('self.struct_' + reflect_on.capitalize(
                                            ) + '.setChecked(True)')

        self._area_light_reflection()

    def area_opacity(self, alpha=0.1, show=True):
        """Set the level of transparency of the deep structures.

        Kargs:
            alpha: float, optional, (def: 0.1)
                Transparency level (usually between 0 and 1).

            show: bool, optional, (def: True)
                Specify if area(s) has be shown.

        Example:
            >>> # Define a vbrain instance :
            >>> vb = vbrain()
            >>> # Set transparency :
            >>> vb.area_opacity(alpha=0.1, show=True)
            >>> # Show the GUI :
            >>> vb.show()
        """
        # Force to have internal projection :
        self.area.mesh.projection('internal')
        self.area.mesh.visible = show
        self.strcutShow.setChecked(show)
        self.area.mesh.set_alpha(alpha)
