"""This file contains user dedicated functions for a direct interaction.

Those functions are a the top level of a visbrain instance and are defined in
order to run commands without the necessity of opening the interface. This is
really convenient for generating a large number of pictures by looping over a
Brain instance.
"""
import logging

import numpy as np
from scipy.spatial import ConvexHull

from ..visuals import BrainMesh
from ..utils import (color2vb, extend_combo_list, safely_set_cbox,
                     get_combo_list_index, safely_set_spin, safely_set_slider)
from ..io import save_config_json, write_fig_canvas

logger = logging.getLogger('visbrain')

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
    def rotate(self, fixed='top', custom=None):
        """Rotate the scene elements using a predefined or a custom rotation.

        The rotation is applied on every objects on the scene.

        Parameters
        ----------
        fixed : str | 'top'
            Use a fixed rotation :

                * Top view : 'top' or 'axial_0'
                * Bottom view : 'bottom' or 'axial_1'
                * Left : 'left' or 'sagittal_0'
                * Right : 'right' or 'sagittal_1'
                * Front : 'front' or 'coronal_0'
                * Back : 'back' or 'coronal_1'
        custom : tuple | None
            Custom rotation. This parameter must be a tuple of two floats
            respectively describing the (azimuth, elevation).

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
        self.atlas.rotate(fixed=fixed, custom=custom)

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
    def brain_control(self, template=None, hemisphere=None, translucent=None,
                      alpha=None, visible=True):
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
        translucent : bool | None
            Set the brain translucent (True) or opaque (False).
        alpha : float | None
            Transparency level.
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
        _brain_update = False
        # Template :
        if template in self.brain_list():
            safely_set_cbox(self._brain_template, template,
                            [self._fcn_brain_template])
            _brain_update = True
        # Hemisphere :
        if hemisphere in ['left', 'both', 'right']:
            safely_set_cbox(self._brain_hemi, hemisphere,
                            [self._fcn_brain_template])
            _brain_update = True
        # Transparent / opaque :
        if isinstance(translucent, bool):
            self._brain_translucent.setChecked(translucent)
            self._fcn_brain_translucent()
        # Opacity :
        if isinstance(alpha, (int, float)):
            self._brain_alpha.setValue(alpha * 100.)
            self._fcn_brain_alpha()
        # Visible :
        self.menuDispBrain.setChecked(visible)
        self._brain_grp.setChecked(visible)
        self._fcn_brain_visible()
        # Update :
        if _brain_update:
            self._fcn_brain_template()

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
        return self.atlas._get_all_available_templates()

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
        self._proj_obj[name] = AddMesh(self._userobj[name])

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
    def sources_control(self, name, data=None, color=None, symbol=None,
                        radius_min=None, radius_max=None, edge_color=None,
                        edge_width=None, alpha=None, mask=None,
                        mask_color=None, visible=True):
        """Set data to sources and control source's properties.

        See the definition of SourceObj for the description of input
        parameters.

        See also
        --------
        sources_display : Select sources to display.
        """
        obj = self.sources[name]
        obj.data = data
        obj.color = color
        obj.symbol = symbol
        obj.radius_min = radius_min
        obj.radius_max = radius_max
        obj.edge_color = edge_color
        obj.edge_width = edge_width
        obj.mask = mask
        obj.mask_color = mask_color
        obj.alpha = alpha
        obj.visible = visible

    def sources_display(self, name=None, select='all'):
        """Select sources to display.

        Parameters
        ----------
        name : string | None
            Name of the source object to control. If None, the selection is
            applied to all sources.
        select : {'all', 'none', 'left', 'right', 'inside', 'outside'}
            The select parameter can be 'all', 'none', 'left', 'right',
            'inside' or 'outside'.

        See also
        --------
        sources_control : Set data to sources and control source's properties.
        """
        if name is None:
            obj = self.sources
        else:
            obj = self.sources[name]
        if select in ['all', 'none', 'left', 'right', None]:
            obj.set_visible_sources(select=select)
        elif select in ['inside', 'outside']:
            vert = self.atlas.vertices
            obj.set_visible_sources(select=select, v=vert)

    def cortical_projection(self, radius=10., project_on='brain',
                            contribute=False, mask_color='orange', **kwargs):
        """Project sources activity.

        This method can be used to project the sources activity either onto the
        brain or on region of interest.

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
        mask_color : string/tuple/array_like | 'orange'
            The color to assign to vertex for masked sources.
        kwargs : dict
            Further arguments are be passed to the cbar_control method.

        See also
        --------
        cortical_repartition : project number of contributing sources.
        roi_control : add a region of interest.
        sources_colormap : Change the colormap properties.
        """
        self._s_proj_radius.setValue(float(radius))
        self._s_proj_contribute.setChecked(contribute)
        self._s_proj_type.setCurrentIndex(0)
        self._s_proj_mask_color.setText(str(mask_color))
        safely_set_cbox(self._s_proj_on, project_on)
        # Colormap control :
        self._fcn_source_proj()
        self.cbar_control('Projection', **kwargs)

    def cortical_repartition(self, radius=10., project_on='brain',
                             contribute=False, mask_color='orange', **kwargs):
        """Project the number of contributing sources per vertex.

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
        mask_color : string/tuple/array_like | 'orange'
            The color to assign to vertex for masked sources.
        kwargs : dict
            Further arguments are be passed to the cbar_control method
        """
        self._s_proj_radius.setValue(float(radius))
        self._s_proj_contribute.setChecked(contribute)
        self._s_proj_type.setCurrentIndex(1)
        self._s_proj_mask_color.setText(str(mask_color))
        safely_set_cbox(self._s_proj_on, project_on)
        # Colormap control :
        self._fcn_source_proj()
        self.cbar_control('Projection', **kwargs)

    def sources_fit_to_vertices(self, name=None, fit_to='brain'):
        """Force sources coordinates to fit to a selected object.

        Parameters
        ----------
        name : string | None
            If name is None, all sources across objects are going to be used.
        fit_to : {'brain', 'roi'}
            The object name to fit. Use 'brain' or 'roi'.
        """
        obj = self.sources[name] if name is not None else self.sources
        v = self._get_obj_vertices(fit_to)
        obj.fit_to_vertices(v)

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

    # =========================================================================
    # =========================================================================
    #                            TIME-SERIES
    # =========================================================================
    # =========================================================================
    def time_series_control(self, name, color=None, line_width=None,
                            amplitude=None, width=None, translate=None,
                            visible=True):
        """Control time-series settings.

        Parameters
        ----------
        name : string
            Name of the time-series object to control.
        color : string/list/tuple/array_like | None
            Color of the time-series.
        amplitude : float | None
            Graphical amplitude of the time-series.
        width : float | None
            Graphical width of th time-series.
        line_width : float | None
            Line width of the time-series.
        translate : tuple | None
            Translation along the (x, y, z) axis for the time-series.
        """
        obj = self.tseries[name]
        obj.color = color
        obj.line_width = line_width
        obj.amplitude = amplitude
        obj.width = width
        obj.translate = translate
        obj.visible_obj = visible

    # =========================================================================
    # =========================================================================
    #                             PICTURES
    # =========================================================================
    # =========================================================================
    def pictures_control(self, name, width=None, height=None, translate=None,
                         visible=True, **kwargs):
        """Control pictures settings.

        Parameters
        ----------
        width : float | 7.
            Width of each picture.
        height : float | 7.
            Height of each picture.
        translate : tuple | None
            Offset along the (x, y, z) axis for the pictures.
        kwargs : dict | {}
            Further arguments can be used to control the colorbar (clim, cmap,
            vmin, under, vmax, over).
        """
        obj = self.pic[name]
        obj.width = width
        obj.height = height
        obj.translate = translate
        obj.visible_obj = visible
        self.cbar_control(name, **kwargs)

    # =========================================================================
    # =========================================================================
    #                            CONNECTIVITY
    # =========================================================================
    # =========================================================================
    def connect_control(self, name, color_by=None, dynamic=None, alpha=None,
                        line_width=None, visible=True, **kwargs):
        """Update connectivity object.

        Parameters
        ----------
        name : string
            Name of the connectivity object to control.
        colorby : string | {'strength', 'count'}
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
            Further arguments can be used to control the colorbar (clim, cmap,
            vmin, under, vmax, over).

        See also
        --------
        cbar_control : control the colormap of a specific object
        """
        obj = self.connect[name]
        obj.color_by = color_by
        obj.dynamic = dynamic
        obj.alpha = alpha
        obj.line_width = line_width
        obj.visible_obj = visible
        self.cbar_control(name, **kwargs)

    # =========================================================================
    # =========================================================================
    #                                 ROI
    # =========================================================================
    # =========================================================================
    def roi_control(self, selection=[], roi_type='Brodmann', smooth=3,
                    name='roi', translucent=False, alpha=None):
        """Select Region Of Interest (ROI) to plot.

        Parameters
        ----------
        selection : list | []
            List of integers where each one refer to a particular roi. The
            corresponding list can be found in the graphical interface in
            the ROI tab or using the function roi_list.
        roi_type : {'Brodmann', 'AAL', 'Talairach'}
            Select the sub-division method i.e 'Brodmann' (for brodmann areas)
            or 'AAL' (Anatomical Automatic Labeling) or 'Talairach'.
        smoth : int | 3
            Define smooth proportion.
        name : string | 'roi'
            Name of the displayed ROI.

        See also
        --------
        roi_list : display the list of supported areas.
        """
        # Check ROI selection :
        if not isinstance(selection, list) and bool(selection):
            raise ValueError("The selection parameter must be a list of "
                             "integers")
        selection = np.unique(selection)
        logger.info("Select {} ROI of {} template".format(selection, roi_type))
        # Select roi_type in the combo list :
        idx = get_combo_list_index(self._roiDiv, roi_type)
        self._roiDiv.setCurrentIndex(idx)
        # Update the list of structures :
        self._fcn_build_roi_list()
        # Set selection :
        self._fcn_set_selected_rois(selection)
        # Apply selection :
        self._fcn_apply_roi_selection(name)
        # Add ROI to mesh list :
        self._proj_obj[name] = self.volume
        self._fcn_update_proj_list()
        self.volume.mesh.translucent = translucent
        self.volume.mesh.alpha = alpha

    def roi_list(self, roi_type='Brodmann'):
        """Get the list of supported ROI.

        Parameters
        ----------
        roi_type : str | 'Brodmann'
            Select the sub-division method i.e 'Brodmann' (for brodmann areas)
            or 'AAL' (Anatomical Automatic Labeling)

        Returns
        -------
        roi_labels : array_like
            The currently supported ROI's labels.
        """
        return self.volume._vols[roi_type].roi_labels

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
        # kwargs['isvmin'] = isinstance(kwargs.get('vmin', None), (int, float))
        # kwargs['isvmax'] = isinstance(vmax, (int, float))
        # Test if the item "name" is enabled :
        self._cbar_item_is_enable(name)
        # Select the object :
        self.cbqt.select(name)
        # Define a CbarBase instance :
        for k, i in kwargs.items():
            if i is not None:
                self.cbqt.cbobjs._objs[name][k] = i
        self.cbqt._fcn_change_object()

    def cbar_select(self, name, visible=True):
        """Select and display a colorbar.

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
        self._fcn_menu_disp_cbar()

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
        self.cbqt._fcn_cb_autoscale(name=name)

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
