"""Top level class for managing the MNI (rotation, structure...).

Make the bridge between GUI and deep functions. Add some usefull
commands for the user
"""
import numpy as np
import logging
from PyQt5 import QtCore

from ....utils import mpl_cmap, mpl_cmap_index


logger = logging.getLogger('visbrain')


class UiAtlas(object):
    """Link graphical interface with atlas functions.

    This class can be used to control the part of displayed brain (both / left
    / right hemisphere), the scene rotation and the light behavior.
    """

    def __init__(self):
        """Init."""
        self._3dobj_type_lst.currentIndexChanged.connect(self._fcn_3dobj_type)

        #######################################################################
        #                              BRAIN
        #######################################################################
        # Visible :
        self._brain_grp.clicked.connect(self._fcn_brain_visible)
        # Template :
        all_templates = self.atlas._get_all_available_templates()
        if self.atlas.name in all_templates:
            self._brain_template.addItems(all_templates)
            idx = all_templates.index(self.atlas.name)
            self._brain_template.setCurrentIndex(idx)
            self._brain_template.currentIndexChanged.connect(
                self._fcn_brain_template)
        # Hemisphere :
        self._brain_hemi.currentIndexChanged.connect(self._fcn_brain_template)
        # Translucent :
        self._brain_translucent.setChecked(self.atlas.translucent)
        self._brain_translucent.clicked.connect(self._fcn_brain_translucent)
        self._brain_alpha.valueChanged.connect(self._fcn_brain_alpha)

        #######################################################################
        #                         REGION OF INTEREST
        #######################################################################
        # Volume selection :
        self._roiDiv.currentIndexChanged.connect(self._fcn_build_roi_list)
        # Apply and reset :
        self._roiButRst.clicked.connect(self._fcn_reset_roi_list)
        self._roiButApply.clicked.connect(self._fcn_apply_roi_selection)
        # Internal/external projection :
        self._roiTransp.clicked.connect(self._fcn_area_translucent)
        self._fcn_build_roi_list()

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

    def _fcn_3dobj_type(self):
        """Change the 3-D object type."""
        self._3dobj_stack.setCurrentIndex(self._3dobj_type_lst.currentIndex())

    def _fcn_gui_rotation(self):
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

    ###########################################################################
    ###########################################################################
    #                                 BRAIN
    ###########################################################################
    ###########################################################################
    def _fcn_brain_visible(self):
        """Display / hide the brain."""
        self.atlas.visible_obj = self._brain_grp.isChecked()

    def _fcn_brain_template(self):
        """Control the type of brain to use."""
        # _____________________ TEMPLATE _____________________
        template = str(self._brain_template.currentText())
        hemisphere = str(self._brain_hemi.currentText())
        logger.info(("Loading %s hemisphere of %s brain "
                     "template") % (hemisphere, template))
        self.atlas.set_data(name=template, hemisphere=hemisphere)
        self.atlas.rotate('top')
        self.atlas.scale = self._gl_scale

    def _fcn_brain_translucent(self):
        """Use translucent or opaque brain."""
        viz = self._brain_translucent.isChecked()
        self.atlas.translucent = viz
        self._brain_alpha.setEnabled(viz)
        self._fcn_brain_alpha()

    def _fcn_brain_alpha(self):
        """Update brain transparency."""
        self.atlas.alpha = self._brain_alpha.value() / 100.

    ###########################################################################
    ###########################################################################
    #                          REGION OF INTEREST
    ###########################################################################
    ###########################################################################
    def _fcn_build_roi_list(self):
        """Build a list of checkable ROIs."""
        # Select volume :
        self.volume.select_volume(str(self._roiDiv.currentText()))
        # Clear widget list and add ROIs :
        self._roiToAdd.clear()
        self._roiToAdd.addItems(self.volume.roi_labels)
        # By default, uncheck items :
        for num in range(self._roiToAdd.count()):
            item = self._roiToAdd.item(num)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)

    def _fcn_reset_roi_list(self):
        """Reset ROIs selection."""
        # Unchecked all ROIs :
        for num in range(self._roiToAdd.count()):
            item = self._roiToAdd.item(num)
            item.setCheckState(QtCore.Qt.Unchecked)

    def _fcn_get_selected_rois(self):
        """Get the list of selected ROIs."""
        _roiToAdd = []
        for num in range(self._roiToAdd.count()):
            item = self._roiToAdd.item(num)
            if item.checkState():
                _roiToAdd.append(num)
        return _roiToAdd

    def _fcn_set_selected_rois(self, selection):
        """Set a list of selected rois."""
        for k in selection:
            item = self._roiToAdd.item(k)
            item.setCheckState(QtCore.Qt.Checked)

    def _fcn_apply_roi_selection(self):
        """Apply ROI selection."""
        # Get the list of selected ROIs :
        _roiToAdd = self._fcn_get_selected_rois()

        if _roiToAdd:
            self.volume._select_roi = self.volume.roi_values[_roiToAdd]
            # Get smoothing :
            self.volume._smooth_roi = self._roiSmooth.value()
            # Plot areas and set parent :
            self.volume.plot_roi()
            self.volume.mesh.parent = self.volume._node
            self._proj_obj['roi'] = self.volume
            self.volume.set_roi_camera(self.view.wc.camera)
            # Enable projection on ROI and related buttons :
            self._s_proj_on.model().item(1).setEnabled(True)
            self._roiTransp.setEnabled(True)
            self.menuDispROI.setEnabled(True)
            self.menuDispROI.setChecked(True)
            self._fcn_area_translucent()
        else:
            raise ValueError("No ROI selected.")

    def _fcn_area_translucent(self, *args):
        """Use opaque / translucent roi."""
        self.volume.mesh.translucent = self._roiTransp.isChecked()

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
        # Set background color :
        bgd = self.view.canvas.bgcolor.rgb
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
        self._fcn_menu_disp_crossec()

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
            self._volIsoTh.setEnabled(True)
            kwargs['threshold'] = self._volIsoTh.value()
        else:
            self._volIsoTh.setEnabled(False)
        # Set this data volume :
        self.volume.set_vol_data(**kwargs)
        # Set visibility :
        viz = self.grpVol.isChecked()
        self.volume.visible_vol = viz
        self.menuDispVol.setChecked(viz)
        self.volume.update()
