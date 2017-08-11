"""Top level class for managing the MNI (rotation, structure...).

Make the bridge between GUI and deep functions. Add some usefull
commands for the user
"""
import numpy as np

from ....utils import mpl_cmap, mpl_cmap_index, get_combo_list_index

__all__ = ['uiAtlas']


class uiAtlas(object):
    """Link graphical interface with atlas functions.

    This class can be used to control the part of displayed brain (both / left
    / right hemisphere), the scene rotation and the light behavior.
    """

    def __init__(self):
        """Init."""
        #######################################################################
        #                              BRAIN
        #######################################################################
        # Template :
        self._brainTemplate.addItems(self.atlas._surf_list)
        idx = self.atlas._surf_list.index(self.atlas.template)
        self._brainTemplate.setCurrentIndex(idx)
        self._brainTemplate.currentIndexChanged.connect(self._brain_control)
        # Hemisphere :
        self._brainPickHemi.currentIndexChanged.connect(self._brain_control)
        # Transparent :
        self._brainTransp.clicked.connect(self._light_reflection)

        #######################################################################
        #                         REGION OF INTEREST
        #######################################################################
        # By default, hide the remove button :
        self._roiButRm.hide()
        # Get plot properties :
        self._roiDiv.currentIndexChanged.connect(self._fcn_build_roi_lst)
        # List management :
        self._roiToSelect.itemClicked.connect(self._fcn_select_roi_in_lst)
        self._roiToAdd.itemClicked.connect(self._fcn_select_added_roi)
        self._roiButAdd.clicked.connect(self._fcn_add_struct)
        self._roiButRm.clicked.connect(self._fcn_rmv_struct)
        self._roiButRst.clicked.connect(self._fcn_rst_struct)
        self._struct2add = []
        # Internal/external projection :
        self._roiTransp.clicked.connect(self._area_light_reflection)
        # System :
        self._roiButApply.clicked.connect(self._fcn_apply_roi)
        self._roiButClear.clicked.connect(self._fcn_clear_roi)
        # Color :
        self._fcn_build_roi_lst()

        #######################################################################
        #                           CROSS-SECTIONS
        #######################################################################
        # Set (min, max) for sliders :
        self._fcn_crossec_sl_limits()
        # Sagittal, coronal and axial slider :
        self._csSagit.sliderMoved.connect(self._fcn_crossec_move)
        self._csCoron.sliderMoved.connect(self._fcn_crossec_move)
        self._csAxial.sliderMoved.connect(self._fcn_crossec_move)
        # Subdivision :
        self._csDiv.currentIndexChanged.connect(self._fcn_crossec_change)
        # Cmap :
        self._csCmap.addItems(mpl_cmap())
        idx = mpl_cmap_index(self.volume._cmap_cs)
        self._csCmap.setCurrentIndex(idx[0])
        self._csCmap.currentIndexChanged.connect(self._fcn_crossec_move)
        # Transparency :
        self._csTransp.clicked.connect(self._fcn_crossec_move)
        # Visibility :
        self.grpSec.clicked.connect(self._fcn_crossec_viz)
        # Split view :
        self._csSplit.clicked.connect(self._fcn_crossec_split)

        #######################################################################
        #                           VOLUME
        #######################################################################
        # Subdivision :
        self._volDiv.currentIndexChanged.connect(self._fcn_vol3d_change)
        # Rendering method :
        self._volRendering.currentIndexChanged.connect(self._fcn_vol3d_change)
        # Cmap :
        cmaps = list(self.volume._cmaps.keys())
        self._volCmap.addItems(cmaps)
        self._volCmap.setCurrentIndex(cmaps.index(self.volume._cmap_vol))
        self._volCmap.currentIndexChanged.connect(self._fcn_vol3d_change)
        # Visibility :
        self.grpVol.clicked.connect(self._fcn_vol3d_change)
        # Threshold :
        self._volIsoTh.valueChanged.connect(self._fcn_vol3d_change)
        self._volIsoTh.setKeyboardTracking(False)

    ###########################################################################
    ###########################################################################
    #                                 BRAIN
    ###########################################################################
    ###########################################################################
    def _brain_control(self):
        """Control the type of brain to use."""
        # _____________________ TEMPLATE _____________________
        template = str(self._brainTemplate.currentText())
        hemisphere = str(self._brainPickHemi.currentText())
        self.atlas.set_data(template, hemisphere)

        # _____________________ VISIBLE _____________________
        self.atlas.mesh.visible = self.menuDispBrain.isChecked()

        # _____________________ RELATED _____________________
        self._cleanProj()
        self._fcn_minmax_slice()

        # _____________________ TRANSFORMATION _____________________
        self._vbNode.transform = self.atlas.mesh._btransform
        self._vbNode.update()

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

    ###########################################################################
    ###########################################################################
    #                          REGION OF INTEREST
    ###########################################################################
    ###########################################################################
    def _fcn_select_roi_in_lst(self):
        """Trig when a structure is selected in the list.

        When the user select a structure in the whole list, display the 'add'
        button but hide the 'remove' button.
        """
        self._roiButAdd.show()
        self._roiButRm.hide()

    def _fcn_select_added_roi(self):
        """Trig when a structure is selected in the added list.

        When the user select a structure in the list, of selected areas,
        hide the 'add' button but display the 'remove' button.
        """
        self._roiButAdd.hide()
        self._roiButRm.show()

    # ---------- Add / remove / update / reset elements to the list ----------
    def _fcn_add_struct(self):
        """Trig when the user click on the 'add' button.

        This function will add the selected structre but only if it's not
        already present in the list.
        """
        current_item = [str(k.text())
                        for k in self._roiToSelect.selectedItems()]
        for k in current_item:
            if k not in self._struct2add:
                self._struct2add.append(k)
            self._fcn_update_list()

    def _fcn_rmv_struct(self):
        """Trig when the user click on the 'remove' button.

        This function doesn't need any conditional testing because the 'remove'
        button is only showed when a structure is displayed.
        """
        current_item = str(self._roiToAdd.current_item().text())
        self._struct2add.pop(self._struct2add.index(current_item))
        self._fcn_update_list()

    def _fcn_update_list(self):
        """Update the list of selected areas.

        The list of selected areas has to be updated if the user add / remove
        structures.
        """
        # Update list :
        self._roiToAdd.clear()
        self._struct2add.sort()
        self._roiToAdd.addItems(self._struct2add)

    def _fcn_rst_struct(self):
        """Reset to default the list of selected areas.

        Just clean all selected structures.
        """
        self._roiToAdd.clear()
        self._struct2add = []

    def _fcn_build_roi_lst(self):
        """Build the list of avaible structures.

        The list of avaible structures depends on the choice of the atlas
        (Brodmann or AAL). This function update the list of areas depending on
        this choice.
        """
        # Get selected volume :
        name = str(self._roiDiv.currentText())
        self.volume.select_volume(name)

        # Update list of structures :
        self._roiToSelect.clear()
        self._roiToSelect.addItems(self.volume.roi_labels)
        self._fcn_rst_struct()

    def _fcn_apply_roi(self):
        """Apply the choice of structures and plot them.

        This function get the list of integers preceding each areas, get the
        vertices and finally plot.
        """
        # Select only the integer preceding the structure :
        _roiToAdd = [int(k.split(':')[0]) for k in self._struct2add]
        _roiToAdd.sort()

        # Add to selected areas and plot :
        self.volume._select_roi = self.volume.roi_values[_roiToAdd]
        self._area_plot()

    def _fcn_clear_roi(self):
        """Clear ROI."""
        self.volume.mesh.clean()
        self.volume.mesh.update()

    def _area_plot(self):
        """Area Sub-plotting function."""
        # Get smoothing :
        self.volume._smooth_roi = self._roiSmooth.value()
        # Plot areas and set parent :
        self.volume.plot_roi()
        self.volume.mesh.parent = self.volume._node
        self._tobj['roi'] = self.volume
        self.volume.set_roi_camera(self.view.wc.camera)
        # Enable projection on ROI and related buttons :
        self._uitProjectOn.model().item(1).setEnabled(True)
        self._roiTransp.setEnabled(True)
        self.menuDispROI.setEnabled(True)
        self.o_Areas.setEnabled(True)
        self._area_light_reflection()

    def _area_light_reflection(self, *args):
        """Change how light is refleting onto sub-areas.

        This function can be used to see either the surface only (external) or
        deep voxels inside areas (internal).
        """
        if self._roiTransp.isChecked():
            self.volume.mesh.projection('internal')
            self.o_Areas.setChecked(True)
            self.o_Areas.setEnabled(True)
        else:
            self.volume.mesh.projection('external')
            self.o_Areas.setChecked(False)
            self.o_Areas.setEnabled(False)

    ###########################################################################
    ###########################################################################
    #                            CROSS-SECTIONS
    ###########################################################################
    ###########################################################################
    def _fcn_crossec_sl_limits(self):
        """Define (min, max) of sliders."""
        # Sagittal / Coronal / Axial :
        self._csSagit.setMaximum(self.volume._nx + 5)
        self._csCoron.setMaximum(self.volume._ny + 5)
        self._csAxial.setMaximum(self.volume._nz + 5)

    def _fcn_crossec_move(self):
        """Trigged when a slider move."""
        # Get center position :
        dx = min(max(0, self._csSagit.value()), self.volume._nx)
        dy = min(max(0, self._csCoron.value()), self.volume._ny)
        dz = min(max(0, self._csAxial.value()), self.volume._nz)
        # Transform slices -> position :
        pos = self.volume.transform.map(np.array([dx, dy, dz]))
        # Get selected colormap :
        cmap = str(self._csCmap.currentText())
        # Set new center position :
        bgd = (self.bgd_red.value(), self.bgd_green.value(),
               self.bgd_blue.value())
        # Get transparency level :
        alpha = 1. - float(self._csTransp.isChecked())
        self.volume.set_cs_data(dx, dy, dz, bgcolor=bgd, alpha=alpha,
                                cmap=cmap)
        # Split view
        if self._csSplit.isChecked():
            self.volume.set_csp_data(self.volume.sagit._data,
                                     self.volume.coron._data,
                                     self.volume.axial._data)
            self.volume._set_csp_camera((dx, dy, dz), pos)

    def _fcn_crossec_viz(self):
        """Control cross-sections visibility."""
        self.menuDispCrossec.setChecked(self.grpSec.isChecked())
        self._fcn_menuCrossec()

    def _fcn_crossec_change(self):
        """Change the cross-sections subdivision type."""
        # Get selected volume :
        name = str(self._csDiv.currentText())
        # Select the volume :
        self.volume.select_volume(name)
        # Update clim and minmax :
        self._fcn_crossec_sl_limits()
        self._fcn_crossec_move()

    def _fcn_crossec_split(self):
        """Toggle split view."""
        if self._csSplit.isChecked():  # Split view
            self._objsPage.setCurrentIndex(1)
            # self.view.canvas.show(False)
            # [k.canvas.show(True) for k in self._csView]
        else:  # Intersection
            self._objsPage.setCurrentIndex(0)
            self.view.canvas.show(True)
            # [k.canvas.show(False) for k in self._csView]
        self._fcn_crossec_move()

    ###########################################################################
    ###########################################################################
    #                                 VOLUME
    ###########################################################################
    ###########################################################################
    def _fcn_vol3d_change(self):
        """Change volume."""
        # Get selected volume :
        name = str(self._volDiv.currentText())
        # Change volume if this volume changed :
        kwargs = {'update': self.volume.name != name}
        if kwargs['update']:
            # Select the volume :
            self.volume.select_volume(name)
        # Get rendering method :
        kwargs['method'] = str(self._volRendering.currentText())
        # Get colormap :
        kwargs['cmap'] = str(self._volCmap.currentText())
        # Set threshold :
        if kwargs['method'] == 'iso':
            kwargs['threshold'] = self._volIsoTh.value()
            self._volIsoTh.setEnabled(True)
        else:
            self._volIsoTh.setEnabled(False)
        # Set this data volume :
        self.volume.set_vol_data(**kwargs)
        # Set visibility :
        viz = self.grpVol.isChecked()
        self.volume.visible_vol = viz
        self.menuDispVol.setChecked(viz)
        self.volume.update()
