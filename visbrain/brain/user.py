"""This file contains user dedicated functions for a direct interaction.

Those functions are a the top level of a visbrain instance and are defined in
order to run commands without the necessity of opening the interface. This is
really convenient for generating a large number of pictures by looping over a
Brain instance.
"""
import numpy as np
from scipy.spatial import ConvexHull

from ..visuals import BrainMesh
from .base.SourcesBase import SourcesBase
from .base.ConnectBase import ConnectBase
from .base.TimeSeriesBase import TimeSeriesBase
from .base.PicBase import PicBase
from ..utils import (color2vb, extend_combo_list, safely_set_cbox,
                     get_combo_list_index, safely_set_spin, safely_set_slider,
                     set_if_not_none)
from ..io import save_config_json, write_fig_canvas

__all__ = ('BrainUserMethods')


class AddMesh(object):
    """Add a mesh object."""

    def __init__(self, mesh):
        """Init."""
        self.mesh = mesh


class BrainUserMethods(object):
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

        Parameters
        ----------
        fixed : string | 'axial'
            Predefined rotation. Use either 'axial', 'coronal' or
            'sagittal'. As a complement, use the suffixe '_0' or
            '_1' to switch between possible views.

            * 'axial_0/1': switch between top/bottom view
            * 'coronal_0/1': switch between front/back view
            * 'sagittal_0/1': switch between left/right view

        custom : tuple | None
            Custom rotation. The custom parameter must be a
            tuple of two float respectively for azimuth and
            elevation.

        Examples
        --------
        >>> # Define a Brain instance :
        >>> vb = Brain()
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

        Parameters
        ----------
        color : tuple/string | (.1, .1, .1)
            The color to use for the background color of the main canvas.
            The color can either be a tuple of integers (R, G, B),
            a matplotlib color (string) or a hexadecimal color (string).

        Examples
        --------
        >>> # Define a Brain instance :
        >>> vb = Brain()
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

    def screenshot(self, saveas, canvas='main', print_size=None, dpi=300.,
                   unit='centimeter', factor=None, region=None, autocrop=False,
                   bgcolor=None, transparent=False):
        """Take a screeshot of the selected canvas.

        By default, the rendered canvas will have the size of your screen.
        The screenshot() method provides two ways to increase to exported image
        resolution :

            * Using print_size, unit and dpi inputs : specify the size of the
              image at a specific dpi level. For example, you might want to
              have an (10cm, 15cm) image at 300 dpi.
            * Using the factor input : multiply the default image size by this
              factor. For example, if you have a (1920, 1080) monitor and if
              factor is 2, the exported image should have a shape of
              (3840, 2160) pixels.

        Parameters
        ----------
        saveas : str
            The name of the file to be saved. This file must contains a
            extension like .png, .tiff, .jpg...
        canvas : {'main', 'colorbar', 'cross-sections'}
            The name of the canvas to render. Use 'main' to select the main
            canvas where the brain is displayed. Use 'colorbar' to render the
            colorbar or 'cross-sections' to render the cross-sections panel
            (in splitted view).
        print_size : tuple | None
            The desired print size. This argument should be used in association
            with the dpi and unit inputs. print_size describe should be a tuple
            of two floats describing (width, height) of the exported image for
            a specific dpi level. The final image might not have the exact
            desired size but will try instead to find a compromize
            regarding to the proportion of width/height of the original image.
        dpi : float | 300.
            Dots per inch for printing the image.
        unit : {'centimeter', 'millimeter', 'pixel', 'inch'}
            Unit of the printed size.
        factor : float | None
            If you don't want to use the print_size input, factor simply
            multiply the resolution of your screen.
        region : tuple | None
            Select a specific region. Must be a tuple of four integers each one
            describing (x_start, y_start, width, height).
        autocrop : bool | False
            Automaticaly crop the figure in order to have the smallest
            space between the brain and the border of the picture.
        bgcolor : array_like/string | None
            The background color of the image.
        transparent : bool | False
            Specify if the exported figure have to contains a transparent
            background.

        Examples
        --------
        >>> # Define a Brain instance :
        >>> vb = Brain()
        >>> # Export the main brain as a (10cm, 20cm) image at 300 dpi:
        >>> vb.screenshot('main.png', canvas='brain', print_size=(10, 20))
        """
        kwargs = {'print_size': print_size, 'dpi': dpi, 'factor': factor,
                  'autocrop': autocrop, 'unit': unit, 'region': region,
                  'bgcolor': bgcolor, 'transparent': transparent}
        if canvas == 'main':
            # Be sure to display the canvas :
            self._objsPage.setCurrentIndex(0)
            self.view.canvas.show(True)
            canvas, widget = self.view.canvas, self.view.wc
        elif canvas == 'colorbar':
            # Display colorbar :
            self.cbpanelW.setVisible(True)
            canvas = self.cbqt.cbviz._canvas
            widget = self.cbqt.cbviz._wc
        elif canvas == 'cross-sections':
            # Be sure to display the canvas :
            self._objsPage.setCurrentIndex(1)
            self._csView.canvas.show(True)
            canvas = self._csView.canvas
            widget = self._csGrid['grid']
        else:
            raise ValueError("The canvas " + canvas + " doesn't exist. Use "
                             "either 'main', 'colorbar' or 'cross-sections'")

        # Render the canvas :
        write_fig_canvas(saveas, canvas, widget, **kwargs)

    def quit(self):
        """Quit the interface."""
        self._app.quit()

    def load_config(self, config):
        """Load a configuration file.

        Parameters
        ----------
        config : string
            File name of the configuration file.
        """
        self._fcn_loadConfig('', filename=config)

    def save_config(self, config):
        """Save a configuration file.

        Parameters
        ----------
        config : string
            File name of the configuration file.
        """
        self._fcn_saveConfig('', filename=config)

    # =========================================================================
    # =========================================================================
    #                                  BRAIN
    # =========================================================================
    # =========================================================================
    def brain_control(self, template=None, hemisphere=None, transparent=None,
                      alpha=None, color=None, visible=True):
        """Control the type of brain to use.

        Use this method to switch between several brain templates. Then, you
        can to display selected hemisphere (left or right).

        Parameters
        ----------
        template : string | None
            Template to use for the MNI brain. Use either 'B1', 'B2' or
            'B3'.
        visible : bool | True
            Show (True) or hide (False) the MNI brain.
        hemisphere : {'both', 'left', 'ritgh'}
            Define if you want to see only 'left' or 'right' hemisphere.
            Otherwise use 'both'.
        transparent : bool | None
            Set the brain transparent (True) or opaque (False).
        alpha : float | None
            Transparency level.
        color : string/tuple | None
            Brain color.
        visible : bool | True
            Display or hide the brain.

        Examples
        --------
        >>> # Define a Brain instance :
        >>> vb = Brain()
        >>> # Display the right hemisphere of 'B3' template :
        >>> vb.brain_control(template='B3', hemisphere='right')
        >>> # Show the GUI :
        >>> vb.show()

        See also
        --------
        brain_list : Get the list of available mesh brain templates.
        """
        _brain_update = _light_update = False
        # Template :
        if template in self.brain_list():
            safely_set_cbox(self._brainTemplate, template,
                            [self._brain_control])
            _brain_update = True
        # Hemisphere :
        if hemisphere in ['both', 'left', 'right']:
            safely_set_cbox(self._brainPickHemi, hemisphere,
                            [self._brain_control])
            _brain_update = True
        # Opacity :
        if isinstance(alpha, (int, float)):
            self.atlas.mesh.projection('internal')
            self.atlas.mesh.set_alpha(alpha)
        # Transparent / opaque :
        if isinstance(transparent, bool):
            self._brainTransp.setChecked(transparent)
            _light_update = True
        # Visible :
        self.menuDispBrain.setChecked(visible)
        self.atlas.mesh.visible = visible
        # Update :
        if _brain_update:
            self._brain_control()
        if _light_update:
            self._light_reflection()
        # Color :
        if color is not None:
            self.atlas.mesh.set_color(color=color)

    def brain_list(self):
        """Get the list of available mesh brain templates.

        Returns
        -------
        meshes : list
            List of available mesh brain templates.

        Examples
        --------
        >>> # Define a Brain instance :
        >>> vb = Brain()
        >>> print(vb.brain_list())
        """
        return self.atlas._surf_list

    def add_mesh(self, name, vertices, faces, **kwargs):
        """Add a mesh to the scene.

        Parameters
        ----------
        name : string
            Name of the object to add.
        vertices : array_like
            Vertices of the mesh.
        faces : array_like
            Faces of the mesh.
        kargs : dict | {}
            Supplementar arguments pass to the BrainMesh class.
        """
        # Add mesh to user objects :
        self._userobj[name] = BrainMesh(vertices=vertices, faces=faces,
                                        name=name, **kwargs)
        self._userobj[name].set_camera(self.view.wc.camera)
        self._userobj[name].parent = self._vbNode
        # Add mesh for projection :
        self._tobj[name] = AddMesh(self._userobj[name])

    def add_volume(self, name, vol, transform=None, roi_values=None,
                   roi_labels=None):
        """Add a new volume to the interface.

        When a new volume is added, it can be then used in the Cross-sections,
        Volume or ROI part if the roi_values and roi_labels are not None.

        Parameters
        ----------
        name : string
            Name of the cross-section object.
        vol : array_like
            The 3-D volume array.
        transform : VisPy.transform | None
            The transformation to add to this volume.
        roi_labels : array_like | None
            Array of strings describing the name of each ROI.
        roi_values : array_like | None
            Array of values describing values of each ROI.

        See also
        --------
        volume_list : Get the list of volumes available.
        """
        # Add the volume :
        self.volume.add_volume(name, vol, transform=transform,
                               roi_values=roi_values, roi_labels=roi_labels)

        # Extend the list of volumes for 3-D volume and cross-section :
        extend_combo_list(self._csDiv, name, self._fcn_crossec_change)
        extend_combo_list(self._volDiv, name, self._fcn_vol3d_change)

        # Extend the list of ROI volumes if possible :
        if self.volume._vols[name]._is_roi:
            # Set label to "N: " + label :
            label = self.volume._labels_to_gui(roi_labels)
            self.volume._vols[name].roi_labels = label
            # Extend ROI combo list :
            extend_combo_list(self._roiDiv, name, self._fcn_build_roi_lst)

    def volume_list(self):
        """Get the list of volumes available.

        Returns
        -------
        volume_list : list
            List of volumes availables.
        """
        return list(self.volume._vols.keys())

    def cross_sections_control(self, pos=(0., 0., 0.), center=None,
                               volume='Brodmann', split_view=True,
                               transparent=True, cmap='gray', show_text=True,
                               visible=True):
        """Control the cross-section.

        The three sections (sagittal, coronal and axial) can be defined in two
        ways :

            * Using the _pos_ input for the use of real coordinates.
            * Using the _center_ input to directly use slices.

        Parameters
        ----------
        pos : array_like | (0., 0., 0.)
            The position of the center in the MNI system. This array of float
            positions is then converted into slices usng the inverse transform
            of the selected volume.
        center : type | default
            Array of 3 integers corresponding respectively to the position of
            the sagittal, coronal and axial sections.
        volume : string | 'Brodmann'
            Name of the volume to use. See the volume_list() method to get the
            list of volumes available.
        split_view : bool | True
            If True, the cross-section is splitted into three images. If False,
            the cross-section is directly displayed inside the brain.
        transparent : bool | True
            Use transparent or opaque borders.
        cmap : string | 'gray'
            Name of the colormap to use.
        show_text : bool | True
            Display or hide slice text.
        visible : bool | True
            Set the cross-sections visible.

        See also
        --------
        add_volume : Add a new volume to the interface.
        volume_list : Get the list of volumes available.
        """
        # Set volume :
        safely_set_cbox(self._csDiv, volume, [self._fcn_crossec_change])
        # Get cross-center :
        if center is not None:
            dx, dy, dz = center
        else:
            pos = np.asarray(pos).ravel()
            ipos = self.volume.transform.imap(pos)[0:-1]
            dx, dy, dz = np.round(ipos).astype(int)
        # Set sagittal, coronal and axial sections :
        self.volume._test_cs_range(dx, dy, dz)
        safely_set_slider(self._csSagit, dx, [self._fcn_crossec_move])
        safely_set_slider(self._csCoron, dy, [self._fcn_crossec_move])
        safely_set_slider(self._csAxial, dz, [self._fcn_crossec_move])
        # Set colormap :
        safely_set_cbox(self._csCmap, cmap, [self._fcn_crossec_move])
        # Set split view, transparent and visible :
        self._csSplit.setChecked(split_view)
        self._csTransp.setChecked(transparent)
        self.grpSec.setChecked(visible)
        self.menuDispCrossec.setChecked(visible)
        # Show text :
        self.volume._cspTxtSagit.visible = show_text
        self.volume._cspTxtAxial.visible = show_text
        self.volume._cspTxtCoron.visible = show_text
        # Update the volume to use and split-view :
        self._fcn_crossec_change()
        self._fcn_crossec_split()
        self._fcn_crossec_viz()

    def volume_control(self, volume='Brodmann', rendering='mip',
                       cmap='OpaqueGrays', threshold=0., visible=True):
        """Control the 3-D volume.

        Parameters
        ----------
        volume : string | 'Brodmann'
            Name of the volume to use. See the volume_list() method to get the
            list of volumes available.
        rendering : {'mip', 'translucent', 'additive', 'iso'}
            description
        cmap : {'TransFire', 'OpaqueFire', 'TransGrays', 'OpaqueGrays'}
            Name of the colormap to use.
        threshold : float | 0.
            Volume threshold for 'iso' rendering.
        visible : bool | True
            Display or hide the volume.
        """
        # Set volume :
        if volume in self.volume_list():
            safely_set_cbox(self._volDiv, volume, [self._fcn_vol3d_change])
        # Threshold :
        safely_set_spin(self._volIsoTh, threshold, [self._fcn_vol3d_change],
                        False)
        # Set cmap :
        safely_set_cbox(self._volCmap, cmap, [self._fcn_vol3d_change])
        # Set rendering :
        if rendering in ['mip', 'translucent', 'additive', 'iso']:
            safely_set_cbox(self._volRendering, rendering,
                            [self._fcn_vol3d_change])
        # Visible :
        self.menuDispVol.setChecked(visible)
        self.grpVol.setChecked(visible)
        self._fcn_vol3d_change()

    # =========================================================================
    # =========================================================================
    #                              SOURCES
    # =========================================================================
    # =========================================================================
    def sources_control(self, data=None, color='#ab4652', symbol=None,
                        radiusmin=None, radiusmax=None, edgecolor='white',
                        edgewidth=None, scaling=None, alpha=None, mask=None,
                        maskcolor='gray'):
        """Set data to sources and control source's properties.

        Parameters
        ----------
        data : None
            Vector of data for each source. Le length of this vector must
            be same as the number of sources.
        color : string/list/ndarray | '#ab4652'
            Color of each source sphere. If s_color is a single string,
            all sphere will have the same color. If it's' a list of
            strings, the length must be N. Alternatively, s_color can be a
            (N, 3) RGB or (N, 4) RGBA colors.
        symbol : string | None
            Symbol to use for sources. Allowed style strings are: disc,
            arrow, ring, clobber, square, diamond, vbar, hbar, cross,
            tailed_arrow, x, triangle_up, triangle_down, and star.
        radiusmin/radiusmax : int/float | (None, None)
            Define the minimum and maximum source's possible radius. By
            default if all sources have the same value, the radius will be
            radiusmin.
        edgecolor : string/list/ndarray | 'white'
            Add an edge to sources
        edgewidth : float | None
            Edge width of sources
        scaling : bool | None
            If set to True, marker scales when rezooming.
        alpha : int/float | None
            Transparency of all sources. Must be between 0 and 1.
        mask : ndarray | None
            Vector of boolean values, with the same length as the length of
            xyz. Use this parameter to mask some sources but keep it
            displayed.
        maskcolor : list/tuple | 'gray'
            Color of masked sources when projected on surface.

        Examples
        --------
        >>> # Define a Brain instance with 10 random sources:
        >>> vb = Brain(s_xyz=np.random.randint(-20, 20, (10, 3)))
        >>> # Define some random data :
        >>> data = 100 * np.random.rand(10)
        >>> # Define some color :
        >>> color = ['blue'] * 3 + ['white'] * 3 + ['red'] * 4
        >>> # Set data and properties :
        >>> vb.sources_control(data=data, symbol='x', radiusmin=1.,
        >>>                    radiusmax=20., color=color, edgecolor='orange',
        >>>                    edgewidth=2)
        >>> # Show the GUI :
        >>> vb.show()
        """
        s = self.sources
        # Update only if sources are already plotted :
        if s.xyz is not None:
            # Get inputs :
            s.data = set_if_not_none(s.data, data)
            s.color = color2vb(color)
            s.edgecolor = color2vb(edgecolor)
            s.edgewidth = set_if_not_none(s.edgewidth, edgewidth)
            s.alpha = set_if_not_none(s.alpha, alpha)
            s.scaling = set_if_not_none(s.scaling, scaling)
            radiusmin = 1.5 * radiusmin if radiusmin is not None else radiusmin
            radiusmax = 1.5 * radiusmax if radiusmax is not None else radiusmax
            s.radiusmin = set_if_not_none(s.radiusmin, radiusmin)
            s.radiusmax = set_if_not_none(s.radiusmax, radiusmax)
            s.symbol = set_if_not_none(s.symbol, symbol)
            s.smask = set_if_not_none(s.smask, mask)
            s.smaskcolor = color2vb(maskcolor)

            # Check arguments and update plot:
            s.prepare2plot()
            s.update()
        else:
            raise ValueError("No sources detected. Please, add some sources "
                             "before trying to update data")

    def sources_opacity(self, alpha=1., show=True):
        """Set the level of transparency of sources.

        Parameters
        ----------
        alpha : float | 1.
            Transparency level (usually between 0 and 1).
        show : bool | True
            Specify if sources has be shown.

        Examples
        --------
        >>> # Define a Brain instance with 10 random sources:
        >>> vb = Brain(s_xyz=np.random.randint(-20, 20, (10, 3)))
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

    def sources_display(self, select='all'):
        """Select sources to display.

        The selected sources can be then used to project activity or
        repartition.

        Parameters
        ----------
        select : {'all', 'none', 'left', 'right', 'inside', 'outside'}
            The select parameter can be 'all', 'none', 'left', 'right',
            'inside' or 'outside'.

        Examples
        --------
        >>> # Define a Brain instance with 10 random sources:
        >>> vb = Brain(s_xyz=np.random.randint(-20, 20, (10, 3)))
        >>> # Set transparency :
        >>> vb.sources_display(select='right')
        >>> # Show the GUI :
        >>> vb.show()
        """
        # Display either All / None :
        if select in ['all', 'none', 'left', 'right']:
            self.sources.display(select)

        # Display sources that are either in the inside / outside the brain :
        elif select in ['inside', 'outside']:
            vert = self.atlas.mesh.get_vertices
            self.sources._isInside(vert, select, self.progressbar)

        else:
            raise ValueError("The select parameter must either be 'all', "
                             "'none', 'left', 'right', 'inside' or 'outside'")

    def cortical_projection(self, radius=10., project_on='brain',
                            contribute=False, **kwargs):
        """Project sources activity.

        This method can be used to project the sources activity either onto the
        brain or on deep areas (like gyrus or brodmann areas).

        Parameters
        ----------
        radius : float | 10.
            Projection radius.
        project_on : string | 'brain'
            Define on which object to project the sources activity. Chose
            either 'brain' for projecting the sources activity onto the
            brain or 'roi' to project on region of interest (if defined).
        contribute : bool | False
            Specify if sources contribute on both hemisphere.
        kwargs : dict
            Further arguments are be passed to the cbar_control method.

        Examples
        --------
        >>> # Define a Brain instance with 10 random sources:
        >>> vb = Brain(s_xyz=np.random.randint(-20, 20, (10, 3)))
        >>> # Set transparency :
        >>> vb.sources_opacity(alpha=0.1, show=True)
        >>> # Run the cortical projection :
        >>> vb.cortical_projection()
        >>> # Show the GUI :
        >>> vb.show()

        See also
        --------
        roi_control : add a region of interest.
        sources_colormap : Change the colormap properties.
        """
        # Update variables :
        self._tradius = float(radius)
        self._tprojecton = project_on
        self._tcontribute = contribute
        self._tprojectas = 'activity'
        # Run the corticale projection :
        self._sourcesProjection()
        # Colormap control :
        self.sources_colormap(**kwargs)

    def cortical_repartition(self, radius=10., project_on='brain',
                             contribute=False, **kwargs):
        """Get the number of contributing sources per vertex.

        Parameters
        ----------
        radius : float | 10.
            Projection radius.
        project_on : string | 'brain'
            Define on which object to project the sources repartition.
            Chose either 'brain' for projecting onto the brain or 'roi'
            to project on region of interest (if defined).
        contribute : bool | False
            Specify if sources contribute on both hemisphere.
        kwargs : dict
            Further arguments are be passed to the cbar_control method.

        Examples
        --------
        >>> # Define a Brain instance with 10 random sources:
        >>> vb = Brain(s_xyz=np.random.randint(-20, 20, (10, 3)))
        >>> # Set transparency :
        >>> vb.sources_opacity(alpha=0.1, show=True)
        >>> # Run the cortical projection :
        >>> vb.cortical_repartition()
        >>> # Show the GUI :
        >>> vb.show()
        """
        # Update variables :
        self._tradius = float(radius)
        self._tprojecton = project_on
        self._tcontribute = contribute
        self._tprojectas = 'repartition'
        # Run the corticale repartition :
        self._sourcesProjection()
        # Colormap control :
        self.sources_colormap(**kwargs)

    def sources_colormap(self, **kwargs):
        """Change the colormap of cortical projection / repartition.

        This method can be used to update paramaters of the colormap. But it's
        only going to work if the source's activity has been projected (using
        the cortical projection or repartition).

        Parameters
        ----------
        kwargs : dict | {}
            Further arguments are be passed to the cbar_control method.

        Examples
        --------
        >>> # Define a Brain instance with 10 random sources:
        >>> vb = Brain(s_xyz=np.random.randint(-20, 20, (10, 3)))
        >>> # Define some random data :
        >>> data = 100 * np.random.rand(10)
        >>> # Set data and properties :
        >>> vb.sources_control(data=data)
        >>> # Run the cortical projection :
        >>> vb.cortical_projection()
        >>> # Set colormap proprties :
        >>> vb.sources_colormap(cmap='Spectral', vmin=20, vmax=60,
        >>>                     under='orange', over='black', clim=(10, 80))
        >>> # Show the GUI :
        >>> vb.show()

        See also
        --------
        cbar_control : control the colorbar of a specific object
        cortical_projection : project source activity onto the cortex
        cortical_repartition : project the source's repartition onto the cortex
        """
        self.cbar_control('Projection', **kwargs)

    def sources_fit(self, obj='brain'):
        """Force sources coordinates to fit to a selected object.

        Parameters
        ----------
        obj : {'brain', 'roi'}
            The object name to fit. Use 'brain' or 'roi'.
        """
        # Get vertices of the selected object :
        v = self._findVertices(obj)
        # fit sources to the selected vertices :
        self.sources._fit(v, self.progressbar)

    def sources_to_convex_hull(self, xyz):
        """Convert a set of sources into a convex hull.

        Parameters
        ----------
        xyz : array_like
            Array of sources coordinates of shape (N, 3)

        Returns
        -------
        faces : array_like
            A set of faces than can be then passed to the add_mesh method.

        See also
        --------
        add_mesh : add a mesh to the scene
        """
        return ConvexHull(xyz).simplices

    def add_sources(self, name, **kwargs):
        """Add a supplementar source's object.

        Warning : sources that are adding usnig this methos cannot be controled
        using the GUI.

        Parameters
        ----------
        name : string
            Your source's object name.
        kwargs : dict
            Pass every further arguments starting with "s" (like s_xyz,
            s_data, s_cmap, s_symbol...)

        Examples
        --------
        >>> vb = Brain()
        >>> s_xyz = np.random.randint(-20, 20, (10, 3))
        >>> vb.add_sources(s_xyz=s_xyz, s_radiusmin=10, s_radiusmax=21,
        >>>                s_opacity=.8, s_symbol='x')
        """
        self._userobj[name] = SourcesBase(**kwargs)
        self._userobj[name].mesh.parent = self._vbNode

    # =========================================================================
    # =========================================================================
    #                            TIME-SERIES
    # =========================================================================
    # =========================================================================
    def time_series_control(self, color=None, lw=None, amp=None, width=None,
                            dxyz=None, visible=True):
        """Control time-series settings.

        Parameters
        ----------
        color : string/list/tuple/array_like | None
            Color of the time-series.
        amp : float | None
            Graphical amplitude of the time-series.
        width : float | None
            Graphical width of th time-series.
        lw : float | None
            Line width of the time-series.
        dxyz : tuple | None
            Offset along the (x, y, z) axis for the time-series.
        """
        self.tseries.set_data(color, lw, amp, width, dxyz, visible)
        self.tseries.mesh.update()

    def add_time_series(self, name, ts_xyz, ts_data, **kwargs):
        """Add time-series (TS) object.

        Parameters
        ----------
        name : string
            Name of the TS object.
        ts_xyz : array_like
            Array of (x, y, z) coordinates of shape (n_sources, 3).
        ts_data : array_like
            Array of time-serie's data of shape (n_sources, n_time_points).
        kwargs : dict | {}
            Further arguments starting with *ts_*.
        """
        self._userobj[name] = TimeSeriesBase(ts_xyz, ts_data, **kwargs)
        self._userobj[name].mesh.parent = self._vbNode
        self.grpTs.setEnabled(True)

    # =========================================================================
    # =========================================================================
    #                             PICTURES
    # =========================================================================
    # =========================================================================
    def pictures_control(self, width=None, height=None, dxyz=None, **kwargs):
        """Control pictures settings.

        Parameters
        ----------
        width : float | 7.
            Width of each picture.
        height : float | 7.
            Height of each picture.
        dxyz : float | (0., 0., 1.)
            Offset along the (x, y, z) axis for the pictures.
        kwargs : dict | {}
            Further arguments can be used to control the colorbar (clim, cmap,
            vmin, under, vmax, over).
        """
        self.pic.mesh.set_data(width, height, dxyz, **kwargs)

    def add_pictures(self, name, pic_xyz, pic_data, **kwargs):
        """Add pictures object.

        Parameters
        ----------
        name : string
            Name of the pictures object.
        pic_xyz : array_like
            Array of (x, y, z) coordinates of shape (n_sources, 3).
        pic_data : array_like
            Array of pictures data of shape (n_sources, n_rows, n_cols).
        kwargs : dict | {}
            Further arguments starting with *pic_*.
        """
        self._userobj[name] = PicBase(pic_xyz, pic_data, **kwargs)
        self._userobj[name].mesh.parent = self._vbNode
        self._userobj[name].set_camera(self.view.wc.camera)
        self.grpPic.setEnabled(True)

    # =========================================================================
    # =========================================================================
    #                            CONNECTIVITY
    # =========================================================================
    # =========================================================================
    def connect_control(self, colorby=None, dynamic=None, show=True,
                        **kwargs):
        """Update connectivity object.

        Parameters
        ----------
        colorby : string | {'strength', 'count', 'density'}
            Define how to color connexions. Use 'strength' if the color has
            to be modulate by the connectivity strength. Use 'count' if the
            color depends on the number of connexions per node. Use
            'density'to define colors according to the number of line in a
            sphere of radius c_dradius.
        dynamic : tuple | None
            Control the dynamic opacity. For example, if dynamic=(0, 1),
            strong connections will be more opaque than weak connections.
        show : bool | True
            Display or hide connectivity.
        kwargs : dict | {}
            Further arguments are be passed to the cbar_control method.

        Examples
        --------
        >>> Generate 10 sources :
        >>> nsources = 10
        >>> s_xyz = np.random.randint(-20, 20, (nsources, 3))  # coordinates
        >>> Create a (N, N) matrix of connectivity strength :
        >>> c_connect = np.random.rand(nsources, nsources)
        >>> c_connect[np.tril_indices_from(c_connect)] = 0
        >>> Mask the connectivity matrix for every values <.6 and >.7
        >>> c_connect = np.ma.masked_array(c_connect, mask=True)
        >>> nz = np.where((c_connect > .7) & (c_connect < .6))
        >>> c_connect.mask[nz] = False
        >>> Define a brain instance :
        >>> vb = Brain(s_xyz=s_xyz, c_connect=c_connect)

        See also
        --------
        cbar_control : control the colormap of a specific object
        """
        if colorby is not None:
            self.connect.colorby = colorby
        if dynamic is not None:
            self.connect.dynamic = dynamic
        # Optional parameters are send to cbar_control :
        self.cbar_control('Connectivity', **kwargs)
        self.connect.mesh.visible = show
        self.connect.update()

    def add_connect(self, name, **kwargs):
        """Add a supplementar connectivity object.

        Warning : connectivity lines that are adding usnig this methos cannot
        be controled using the GUI.

        Parameters
        ----------
        name : string
            Your connectivity lines object name.
        kwargs : dict
            Pass every further arguments starting with *c_* (like c_xyz,
            c_connect, c_select, c_colorby...)
        """
        self._userobj[name] = ConnectBase(**kwargs)
        self._userobj[name].mesh.parent = self._vbNode

    # =========================================================================
    # =========================================================================
    #                                 ROI
    # =========================================================================
    # =========================================================================
    def roi_control(self, selection=[], subdivision='Brodmann', smooth=3,
                    name='roi'):
        """Select Region Of Interest (ROI) to plot.

        Parameters
        ----------
        selection : list | []
            List of integers where each one refer to a particular roi. The
            corresponding list can be found in the graphical interface in
            the ROI tab or using the function roi_list.
        subdivision : {'Brodmann', 'AAL'}
            Select the sub-division method i.e 'Brodmann' (for brodmann areas)
            or 'AAL' (Anatomical Automatic Labeling)
        smoth : int | 3
            Define smooth proportion.
        name : string | 'roi'
            Name of the displayed ROI.

        Examples
        --------
        >>> # Define a Brain instance :
        >>> vb = Brain()
        >>> # Display brodmann area 4 and 6 :
        >>> vb.roi_control(selection=[4, 6], subdivision='Brodmann', smooth=5)
        >>> # Show the GUI :
        >>> vb.show()

        See also
        --------
        roi_list : display the list of supported areas.
        """
        # Check ROI selection :
        if not isinstance(selection, list) and bool(selection):
            raise ValueError("The selection parameter must be a list of "
                             "integers")
        selection = np.unique(selection)
        # Select subdivision in the combo list :
        idx = get_combo_list_index(self._roiDiv, subdivision)
        self._roiDiv.setCurrentIndex(idx)
        # Update the list of structures :
        self._fcn_build_roi_list()
        # Set selection :
        self._fcn_set_selected_rois(selection)
        # Apply selection :
        self._fcn_apply_roi_selection()
        # Add ROI to mesh list :
        self._tobj[name] = self.volume
        self._fcn_updateProjList()

    def roi_light_reflection(self, reflect_on=None):
        """Change how light is reflecting onto roi.

        This function can be used to see either the surface only (external) or
        deep voxels inside roi (internal).

        Parameters
        ----------
        reflect_on : {'internal', 'external'}
            Choose either to reflect on 'internal' or 'external'.

        Examples
        --------
        >>> # Define a Brain instance :
        >>> vb = Brain()
        >>> # Display brodmann area 4 and 6 :
        >>> vb.roi_control(selection=[4, 6], subdivision='Brodmann')
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
                self._roiTransp.setChecked(reflect_on == 'internal')

        self._area_light_reflection()

    def roi_opacity(self, alpha=0.1, show=True):
        """Set the level of transparency of the deep structures.

        Parameters
        ----------
        alpha : float | 0.1
            Transparency level (usually between 0 and 1).
        show : bool | True
            Specify if roi(s) has be shown.

        Examples
        --------
        >>> # Define a Brain instance :
        >>> vb = Brain()
        >>> # Display brodmann area 4 and 6 :
        >>> vb.roi_control(selection=[4, 6], subdivision='Brodmann')
        >>> # Set transparency :
        >>> vb.roi_opacity(alpha=0.1, show=True)
        >>> # Show the GUI :
        >>> vb.show()
        """
        # Force to have internal projection :
        self.volume.mesh.projection('internal')
        self.volume.mesh.visible = show
        self.volume.mesh.set_alpha(alpha)

    def roi_list(self, subdivision='Brodmann'):
        """Get the list of supported ROI.

        Parameters
        ----------
        subdivision : str | 'Brodmann'
            Select the sub-division method i.e 'Brodmann' (for brodmann areas)
            or 'AAL' (Anatomical Automatic Labeling)

        Returns
        -------
        roi_labels : array_like
            The currently supported ROI's labels.

        Examples
        --------
        >>> # Define a Brain instance :
        >>> vb = Brain()
        >>> # Get list of ROI for AAL :
        >>> lst = vb.roi_list(subdivision='AAL')
        >>> # Print this list :
        >>> print(lst)
        """
        return self.volume._vols[subdivision].roi_labels

    # =========================================================================
    # =========================================================================
    #                             COLORBAR
    # =========================================================================
    # =========================================================================
    def _cbar_item_is_enable(self, name):
        """Test if an item is enabled.

        Parameters
        ----------
        name : string, {'Projection', 'Connectivity', 'Pictures'}
            Name of the colorbar object. If you want to control the colorbar of
            either the cortical projection, use 'Projection'. And
            'Connectivity' or 'Pictures' if defined.
        """
        availables = self.cbar_list()
        if name in availables:
            # Select the object :
            self.cbqt.select(name)
        else:
            raise ValueError(name + " cannot be controlled. Use "
                             "either : " + ", ".join(availables))

    def cbar_control(self, name, **kwargs):
        """Control the colorbar of a specific object.

        Optional parameters let to None are going to be ignored.

        Parameters
        ----------
        name : string, {'Projection', 'Connectivity', 'Pictures'}
            Name of the colorbar object. If you want to control the colorbar of
            either the cortical projection, use 'Projection'. And
            'Connectivity' or 'Pictures' if defined.
        cmap : string | None
            Matplotlib colormap (like 'viridis', 'inferno'...).
        clim : tuple/list | None
            Colorbar limit. Every values under / over clim will
            clip.
        isvmin : bool | None
            Activate/deactivate vmin.
        vmin : float | None
            Every values under vmin will have the color defined
            using the under parameter.
        isvmax : bool | None
            Activate/deactivate vmax.
        vmax : float | None
            Every values over vmin will have the color defined
            using the over parameter.
        under : tuple/string | None
            Matplotlib color under vmin.
        over : tuple/string | None
            Matplotlib color over vmax.
        cblabel : string | None
            Colorbar label.
        cbtxtsz : float | None
            Text size of the colorbar label.
        cbtxtsh : float | None
            Shift for the colorbar label.
        txtcolor : string | 'white'
            Text color.
        txtsz : float | None
            Text size for clim/vmin/vmax text.
        txtsh : float | None
            Shift for clim/vmin/vmax text.
        border : bool | None
            Display colorbar borders.
        bw : float | None
            Border width.
        limtxt : bool | None
            Display vmin/vmax text.
        bgcolor : tuple/string | None
            Background color of the colorbar canvas.
        ndigits : int | None
            Number of digits for the text.
        """
        # Test if the item "name" is enabled :
        self._cbar_item_is_enable(name)
        # Select the object :
        self.cbqt.select(name)
        # Define a CbarBase instance :
        for k, i in kwargs.items():
            if i is not None:
                self.cbqt.cbobjs._objs[name][k] = i
        self.cbqt._fcn_ChangeObj()

    def cbar_select(self, name, visible=True):
        """Select and disply a colorbar.

        Parameters
        ----------
        name : string, {'Projection', 'Connectivity', 'Pictures'}
            Name of the colorbar object. If you want to control the colorbar of
            either the cortical projection, use 'Projection'. And
            'Connectivity' or 'Pictures' if defined.
        visible : bool | True
            Set the colorbar of the object "name" visible.
        """
        # Test if the item "name" is enabled :
        self._cbar_item_is_enable(name)
        # Select the object :
        self.cbqt.select(name)
        # Display / hide the colorbar :
        self.menuDispCbar.setChecked(visible)
        self._fcn_menuCbar()

    def cbar_list(self):
        """Get the list of objects for which the colorbar can be controlled.

        Returns
        -------
        cbobjs : list
            List of objects for which the colorbar can be controlled.
        """
        obj = self.cbqt.cbui.object
        allitems = [obj.itemText(i) for i in range(
            obj.count()) if obj.model().item(i).isEnabled()]
        return allitems

    def cbar_autoscale(self, name):
        """Autoscale the colorbar to the best limits.

        Parameters
        ----------
        name : string, {'Projection', 'Connectivity', 'Pictures'}
            Name of the colorbar object. If you want to control the colorbar of
            either the cortical projection, use 'Projection'. And
            'Connectivity' or 'Pictures' if defined.
        """
        # Test if the item "name" is enabled :
        self._cbar_item_is_enable(name)
        # Autoscale :
        self.cbqt._fcn_cbAutoscale(name=name)

    def cbar_export(self, filename=None, export_only=None, get_dict=False):
        """Export colorbars in a text file or in a dictionary.

        Parameters
        ----------
        filename : string | None
            Name of the text file (i.e 'name.txt'). If None, colorbars are not
            going to be saved.
        export_only : list | None
            List of names for exporting the colorbar.
        get_dict : bool | False
            Get colorbars as a dictionary.

        Returns
        -------
        dict_all : dict
            Dictionary of all colorbars (only if get_dict is True)
        """
        dict_all = self.cbqt.cbobjs.to_dict(alldicts=True)
        if isinstance(export_only, list):
            config = {}
            for k in export_only:
                config[k] = dict_all[k]
        else:
            config = dict_all
        if isinstance(filename, str):
            save_config_json(filename, config)
        if get_dict:
            return config
