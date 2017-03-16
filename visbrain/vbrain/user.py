"""This file contains user dedicated functions for a direct interaction.

Those functions are a the top level of a visbrain instance and are defined in
order to run commands without the necessity of opening the interface. This is
really convenient for generating a large number of pictures by looping over a
vbrain instance.
"""

import numpy as np
import os.path

from ..utils import color2vb

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

    # =========================================================================
    # =========================================================================
    #                             SETTINGS
    # =========================================================================
    # =========================================================================
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

    # =========================================================================
    # =========================================================================
    #                           BRAIN CONTROL
    # =========================================================================
    # =========================================================================
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

    # =========================================================================
    # =========================================================================
    #                              SOURCES
    # =========================================================================
    # =========================================================================
    def sources_data(self, data, color='#ab4652', symbol='disc', radiusmin=5.,
                     radiusmax=10., edgecolor=None, edgewidth=0.6,
                     scaling=False, opacity=1.0, mask=None, maskcolor='gray'):
        """Set data to sources and control source's properties.

        Args
            data: array
                Vector of data for each source. Le length of this vector must
                be same as the number of sources.

        Kargs:
            color: string/list/ndarray, optional, (def: '#ab4652')
                Color of each source sphere. If s_color is a single string,
                all sphere will have the same color. If it's' a list of
                strings, the length must be N. Alternatively, s_color can be a
                (N, 3) RGB or (N, 4) RGBA colors.

            symbol: string, optional, (def: 'disc')
                Symbol to use for sources. Allowed style strings are: disc,
                arrow, ring, clobber, square, diamond, vbar, hbar, cross,
                tailed_arrow, x, triangle_up, triangle_down, and star.

            radiusmin/radiusmax: int/float, optional, (def: 5.0/10.0)
                Define the minimum and maximum source's possible radius. By
                default if all sources have the same value, the radius will be
                radiusmin.

            edgecolor: string/list/ndarray, optional, (def: None)
                Add an edge to sources

            edgewidth: float, optional, (def: 0.4)
                Edge width of sources

            scaling: bool, optional, (def: True)
                If set to True, marker scales when rezooming.

            opacity: int/float, optional, (def: 1.0)
                Transparency of all sources. Must be between 0 and 1.

            mask: ndarray, optional, (def: None)
                Vector of boolean values, with the same length as the length of
                xyz. Use this parameter to mask some sources but keep it
                displayed.

            maskcolor: list/tuple, optional, (def: 'gray')
                Color of masked sources when projected on surface.

        Example:
            >>> # Define a vbrain instance with 10 random sources:
            >>> vb = vbrain(s_xyz=np.random.randint(-20, 20, (10, 3)))
            >>> # Define some random data :
            >>> data = 100 * np.random.rand(10)
            >>> # Define some color :
            >>> color = ['blue'] * 3 + ['white'] * 3 + ['red'] * 4
            >>> # Set data and properties :
            >>> vb.sources_data(data=data, symbol='x',
            >>>                 radiusmin=1., radiusmax=20., color=color,
            >>>                 edgecolor='orange', edgewidth=2)
            >>> # Show the GUI :
            >>> vb.show()
        """
        # Update only if sources are already plotted :
        if self.sources.xyz is not None:
            # Get inputs :
            self.sources.data = data
            self.sources.color = color
            self.sources.edgecolor = color2vb(edgecolor)
            self.sources.edgewidth = edgewidth
            self.sources.alpha = opacity
            self.sources.scaling = scaling
            self.sources.radiusmin = radiusmin*1.5
            self.sources.radiusmax = radiusmax*1.5
            self.sources.symbol = symbol
            self.sources.smask = mask
            self.sources.smaskcolor = color2vb(maskcolor)

            # Check arguments and update plot:
            self.sources.prepare2plot()
            self.sources.update()
        else:
            raise ValueError("No sources detected. Please, add some sources "
                             "before trying to update data")

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

    def cortical_projection(self, project_on='brain', mask=None):
        """Project sources activity.

        This method can be used to project the sources activity either onto the
        brain or on deep areas (like gyrus or brodmann areas).

        Kargs:
            project_on: string, optional, (def: 'brain')
                Define on which object to project the sources activity. Chose
                either 'brain' for projecting the sources activity onto the
                brain or 'roi' to project on region of interest (if defined).

        Example:
            >>> ...

        See also:
            area_plot, sources_colormap
        """
        if project_on in ['brain', 'roi']:
            self._tprojecton = project_on
        else:
            raise ValueError("The project_on parameter must be either "
                             "'brain' or 'roi'")

        # Run the corticale projection :
        self._cortical_projection()

    def cortical_repartition(self):
        """Get the number of contributing sources per vertex.

        Kargs:

        Example:
            >>>
        """
        self._cortical_repartition()

    def sources_colormap(self, cmap=None, clim=None, vmin=None,
                         under=None, vmax=None, over=None):
        """Change the colormap of cortical projection.

        This method can be used to update paramaters of the colormap. But it's
        only going to work if the source's activity has been projected (using
        the cortical projection or repartition).

        Kargs:
            cmap: string, optional, (def: inferno)
                Matplotlib colormap

            clim: tuple/list, optional, (def: None)
                Limit of the colormap. The clim parameter must be a tuple /
                list of two float number each one describing respectively the
                (min, max) of the colormap. Every values under clim[0] or over
                clim[1] will peaked.

            alpha: float, optional, (def: 1.0)
                The opacity to use. The alpha parameter must be between 0 and
                1.

            vmin: float, optional, (def: None)
                Threshold from which every color will have the color defined
                using the under parameter bellow.

            under: tuple/string, optional, (def: 'dimgray')
                Matplotlib color for values under vmin.

            vmax: float, optional, (def: None)
                Threshold from which every color will have the color defined
                using the over parameter bellow.

            over: tuple/string, optional, (def: 'darkred')
                Matplotlib color for values over vmax.

        Example:
            >>> # Define a vbrain instance with 10 random sources:
            >>> vb = vbrain(s_xyz=np.random.randint(-20, 20, (10, 3)))
            >>> # Define some random data :
            >>> data = 100 * np.random.rand(10)
            >>> # Set data and properties :
            >>> vb.sources_data(data=data)
            >>> # Run the cortical projection :
            >>> vb.cortical_projection()
            >>> # Set colormap proprties :
            >>> vb.sources_colormap(cmap='Spectral', vmin=20, vmax=60,
            >>>                     under='orange', over='black', clim=(10,80))
            >>> # Show the GUI :
            >>> vb.show()

        See also:
            cortical_projection, cortical_repartition
        """
        pass

    # =========================================================================
    # =========================================================================
    #                            CONNECTIVITY
    # =========================================================================
    # =========================================================================

    # =========================================================================
    # =========================================================================
    #                                 ROI
    # =========================================================================
    # =========================================================================
    def roi_plot(self, selection=[], subdivision='brod', smooth=3):
        """Select some roi to plot.

        Kargs:
            selection: list, optional, (def: [])
                List of integers where each one refer to a particular roi. The
                corresponding list can be found in the graphical interface in
                the ROI tab or using the function roi_list.

            subdivision: str, optional, (def: 'brod')
                Select the sub-division method i.e 'brod' (for brodmann areas)
                or 'aal' (Anatomical Automatic Labeling)

            smoth: int, optional, (def: 3)
                Define smooth proportion.

        Example:
            >>> # Define a vbrain instance :
            >>> vb = vbrain()
            >>> # Display brodmann area 4 and 6 :
            >>> vb.roi_plot(selection=[4, 6], subdivision='brod', smooth=5)
            >>> # Show the GUI :
            >>> vb.show()

        See also:
            roi_list
        """
        # Inputs checking :
        if not isinstance(selection, list):
            raise ValueError("The selection parameter must be a list of "
                             "integers")
        if subdivision not in ['brod', 'aal']:
            raise ValueError("The subdivision parameter must either be 'brod' "
                             "or 'aal'")

        # roi selection (only if it's not empty) :
        if selection:
            # Sort selection :
            selection.sort()
            self.area.select = selection
            self.area.structure = subdivision
            self._roiSmooth.setValue(smooth)
            # Plot ROI :
            self._area_plot()
            # --------------- GUI ---------------
            # Set check the corresponding subdivision :
            if subdivision == 'brod':
                self.Sub_brod.setChecked(True)
            elif subdivision == 'aal':
                self.Sub_aal.setChecked(True)
            # Add selected items to the GUI :
            self.struct2add.addItems(self.area._label[np.add(selection, -1)])
            self.struct2select.clear()
            self.struct2select.addItems(self.area._label)

    def roi_light_reflection(self, reflect_on=None):
        """Change how light is reflecting onto roi.

        This function can be used to see either the surface only (external) or
        deep voxels inside roi (internal).

        Kargs:
            reflect_on: string, optional, (def: None)
                Choose either to reflect on 'internal' or 'external'.

        Example:
            >>> # Define a vbrain instance :
            >>> vb = vbrain()
            >>> # Display brodmann area 4 and 6 :
            >>> vb.roi_plot(selection=[4, 6], subdivision='brod')
            >>> # Display the external surface :
            >>> vb.roi_light_reflection(reflect_on='internal')
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

    def roi_opacity(self, alpha=0.1, show=True):
        """Set the level of transparency of the deep structures.

        Kargs:
            alpha: float, optional, (def: 0.1)
                Transparency level (usually between 0 and 1).

            show: bool, optional, (def: True)
                Specify if roi(s) has be shown.

        Example:
            >>> # Define a vbrain instance :
            >>> vb = vbrain()
            >>> # Set transparency :
            >>> vb.roi_opacity(alpha=0.1, show=True)
            >>> # Show the GUI :
            >>> vb.show()
        """
        # Force to have internal projection :
        self.area.mesh.projection('internal')
        self.area.mesh.visible = show
        self.strcutShow.setChecked(show)
        self.area.mesh.set_alpha(alpha)

    def roi_list(self, subdivision='brod'):
        """Get the list of supported ROI.

        Kargs:
            subdivision: str, optional, (def: 'brod')
                Select the sub-division method i.e 'brod' (for brodmann areas)
                or 'aal' (Anatomical Automatic Labeling)

        Return:
            labels: str
                The currently supported ROI's labels.

        Example:
            >>> # Define a vbrain instance :
            >>> vb = vbrain()
            >>> # Get list of ROI for AAL :
            >>> lst = vb.roi_list(subdivision='aal')
            >>> # Print this list :
            >>> print(lst)
        """
        return str(self.area)
