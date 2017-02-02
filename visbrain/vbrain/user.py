"""This file contains user dedicated functions for a direct interaction.

Those functions are a the top level of a visbrain instance and are defined in
order to run commands without the necessity of opening the interface. This is
really convenient for generating a large number of pictures by looping over a
vbrain instance.
"""

from .utils import color2vb
import os.path

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
        """Set the background color of the main canvas and the colorbar.

        The main canvas is defined as the canvas where all objects are
        displayed. The colorbar has it own canvas and the background set will
        be the same as the one of the main canvas.

        Kargs:
            color: tuple/string, optional, (def: (.1, .1, .1))
                The color to use for the background color of the main canvas.
                The color can either be a tuple of integers (R, G, B),
                a matplotlib color (string) or a hexadecimal color (string).

        Example:
            >>> # Define a vbrain instance :
            >>> vb = vbrain()
            >>> # Set the background color (using a RGB tuple) :
            >>> vb.background_color(color=(1., 1., 1.))
            >>> # Set the background color (using matplotlib format) :
            >>> vb.background_color(color='white')
            >>> # Set the background color (using hexadecimal format) :
            >>> vb.background_color(color='#ffffff')
            >>> # Show the GUI :
            >>> vb.show()
        """
        bckcolor = color2vb(color).ravel()[0:-1]
        self.view.canvas.bgcolor = bckcolor
        self.view.cbcanvas.bgcolor = bckcolor

    def screenshot(self, name, region=None, colorbar=False):
        """Take a screenshot of the current scene and save it as a picture.

        This method try to make a high-fidelity screenshot of your scene. There
        might be some strange behaviors (like with connectivity line width).
        One thing to keep in mind, is that printed picture using a transparent
        compatible extension (like .png files) produces transparent pictures.
        This might be quit disturbing especially using internal light
        reflection. To solve this in your pictures, I recommand putting your
        transparent brain picture onto a dark background (like black) and see
        the magic happend.
        This method requires imageio or PIL (pip install pillow).

        Args:
            name: str
                The name of the file to be saved. This file must contains one
                of the following extension: .png, .tiff

        Kargs:
            region: tuple, optional, (def: None)
                Crop the exported picture to a specified region. Must be a
                tuple of four integers where each one describe the region as
                (x_start, y_start, width, height) where x_start is where
                to start along the horizontal axis and y_start where to start
                along the vertical axis. By default, the entire canvas is
                rendered.

            colorbar: bool, optional, (def: False)
                Specify if the colorbar has to be exported too.

        Example:
            >>> # Define a vbrain instance :
            >>> vb = vbrain()
            >>> # Define the filename and the cropped region :
            >>> filename, crop = 'myfile.png', (1000, 300, 570, 550)
            >>> # Rotate the brain :
            >>> vb.rotate('axial')
            >>> # Take a screenshot and save it (tested on a 17" laptop) and
            >>> # export the colorbar :
            >>> vb.screenshot(filename, region=crop, colorbar=True)

        See also:
            .. seealso:: background_color, rotate

        Note:
            .. note:: the region argument can be quit difficult to ajust. Be
                patient, it's possible. Don't forget that .png files contains
                transparency. For an optimal screenshot, I recommand doing a
                rotation before the screenshot, so that the canvas can be
                initialized.
        """
        # Define the filename :
        if isinstance(name, str):
            self._savename, self._extension = os.path.splitext(name)
            self._extension = self._extension.replace('.', '')
        else:
            raise ValueError("The name must be a string and must contains the"
                             " extension (ex: name='myfile.png')")

        # Define the cropped region :
        if region is not None:
            if isinstance(region, (tuple, list)) and (len(region) == 4):
                self._crop = region
            else:
                raise ValueError("The region parameter must be a tuple of four"
                                 " integers describing (x_start, y_start, "
                                 "width, height)")

        # Define if the colorbar has to be exported :
        if isinstance(colorbar, bool):
            self.cb['export'] = colorbar
        else:
            raise ValueError("The colorbar parameter must be a bool describing"
                             " if the colorbar have to exported too.")

        self._screenshot()

    def quit(self):
        """Quit the interface."""
        self._app.quit()

    ###########################################################################
    ###########################################################################
    #                           BRAIN CONTROL
    ###########################################################################
    ###########################################################################
    def brain_control(self, template=None, show=True, hemisphere=None):
        """Control the type of brain to use.

        Use this method to switch between several brain templates. Then, you
        can to display selected hemisphere (left or right).

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

        Note:
            .. note:: The brain opacity is only avaible for internal projection
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

        See also:
            .. seealso:: brain_control, brain_opacity
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
