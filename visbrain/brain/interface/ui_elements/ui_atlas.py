"""Top level class for managing the MNI (rotation, structure...).

Make the bridge between GUI and deep functions. Add some usefull
commands for the user
"""
import numpy as np
import logging
from PyQt5 import QtCore, QtWidgets

from ....objects.volume_obj import VOLUME_CMAPS
from ....utils import mpl_cmap, mpl_cmap_index, fill_pyqt_table


logger = logging.getLogger('visbrain')


class UiAtlas(object):
    """Link graphical interface with atlas functions.

    This class can be used to control the part of displayed brain (both / left
    / right hemisphere), the scene rotation and the light behavior.
    """

    def __init__(self):
        """Init."""
        #######################################################################
        #                              BRAIN
        #######################################################################
        # Visible :
        self._brain_grp.clicked.connect(self._fcn_brain_visible)
        # Template :
        all_templates = self.atlas.list()
        enable_template = self.atlas.name in all_templates
        if enable_template:
            self._brain_template.addItems(all_templates)
            idx = all_templates.index(self.atlas.name)
            self._brain_template.setCurrentIndex(idx)
            self._brain_template.currentIndexChanged.connect(
                self._fcn_brain_template)
            # Hemisphere :
            idx = ['both', 'left', 'right'].index(self.atlas.mesh.hemisphere)
            self._brain_hemi.setCurrentIndex(idx)
            self._brain_hemi.currentIndexChanged.connect(
                self._fcn_brain_hemisphere)
        self._brain_template.setEnabled(enable_template)
        self._brain_hemi.setEnabled(enable_template)
        # Translucent :
        self._brain_translucent.setChecked(self.atlas.translucent)
        self._brain_translucent.clicked.connect(self._fcn_brain_translucent)
        self._brain_alpha.valueChanged.connect(self._fcn_brain_alpha)

        #######################################################################
        #                         REGION OF INTEREST
        #######################################################################
        # Volume selection :
        self._roi_grp.setChecked(self.roi.visible_obj)
        self._roi_grp.clicked.connect(self._fcn_roi_visible)
        self._fcn_roi_visible()
        vol_list = self.roi.list()
        self._roiDiv.addItems(vol_list)
        self._roiDiv.setCurrentIndex(vol_list.index(self.roi.name))
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
        self._csSagit.setValue(self.cross_sec._section[0])
        self._csCoron.setValue(self.cross_sec._section[1])
        self._csAxial.setValue(self.cross_sec._section[2])
        self._csSagit.sliderMoved.connect(self._fcn_crossec_move)
        self._csCoron.sliderMoved.connect(self._fcn_crossec_move)
        self._csAxial.sliderMoved.connect(self._fcn_crossec_move)
        # Subdivision :
        self._csDiv.addItems(vol_list)
        self._csDiv.currentIndexChanged.connect(self._fcn_crossec_change)
        # Cmap :
        self._csCmap.addItems(mpl_cmap())
        idx = mpl_cmap_index(self.cross_sec.to_kwargs()['cmap'])
        self._csCmap.setCurrentIndex(idx[0])
        self._csCmap.currentIndexChanged.connect(self._fcn_crossec_cmap)
        # Visibility :
        self._sec_grp.setChecked(self.cross_sec.visible_obj)
        self._sec_grp.clicked.connect(self._fcn_crossec_viz)
        self._fcn_crossec_viz()

        #######################################################################
        #                           VOLUME
        #######################################################################
        # Subdivision :
        self._volDiv.addItems(vol_list)
        self._volDiv.currentIndexChanged.connect(self._fcn_vol_change)
        # Rendering method :
        self._volRendering.currentIndexChanged.connect(self._fcn_vol_rendering)
        # Cmap :
        cmaps = list(VOLUME_CMAPS.keys())
        self._volCmap.addItems(cmaps)
        self._volCmap.setCurrentIndex(cmaps.index(self.volume.cmap))
        self._volCmap.currentIndexChanged.connect(self._fcn_vol_cmap)
        # Visibility :
        self._vol_grp.setChecked(self.volume.visible_obj)
        self._vol_grp.clicked.connect(self._fcn_vol_visible)
        self._fcn_vol_visible()
        # Threshold :
        self._volIsoTh.valueChanged.connect(self._fcn_vol_threshold)
        self._volIsoTh.setKeyboardTracking(False)

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
        self.menuDispBrain.setChecked(self._brain_grp.isChecked())
        self._fcn_menu_disp_brain()

    def _fcn_brain_template(self):
        """Control the type of brain to use."""
        # _____________________ TEMPLATE _____________________
        template = str(self._brain_template.currentText())
        hemisphere = str(self._brain_hemi.currentText())
        self.atlas.set_data(name=template, hemisphere=hemisphere)
        self.atlas.scale = self._gl_scale
        self.atlas.reset_camera()
        self.atlas.rotate('top')

    def _fcn_brain_hemisphere(self):
        """Change the hemisphere."""
        hemi = str(self._brain_hemi.currentText())
        self.atlas.mesh.hemisphere = hemi

    def _fcn_brain_translucent(self):
        """Use translucent or opaque brain."""
        viz = self._brain_translucent.isChecked()
        self.atlas.translucent = viz
        self._brain_alpha.setEnabled(viz)
        self._fcn_brain_alpha()

    def _fcn_brain_alpha(self):
        """Update brain transparency."""
        alpha = self._brain_alpha.value() / 100.
        self.atlas.alpha = alpha

    ###########################################################################
    ###########################################################################
    #                          REGION OF INTEREST
    ###########################################################################
    ###########################################################################
    def _fcn_roi_visible(self):
        """Display or hide ROI."""
        self.menuDispROI.setChecked(self._roi_grp.isChecked())
        self._fcn_menu_disp_roi()

    def _fcn_build_roi_list(self):
        """Build a list of checkable ROIs."""
        # Select volume :
        selected_roi = str(self._roiDiv.currentText())
        if self.roi.name != selected_roi:
            self.roi(selected_roi)
        # Clear widget list and add ROIs :
        self._roiToAdd.clear()
        df = self.roi.get_labels()
        col_names = [''] + list(df.keys())
        col_names.pop(col_names.index('index'))
        cols = [[''] * len(df)]
        cols += [list(df[k]) for k in col_names if k not in ['', 'index']]
        # By default, uncheck items :
        fill_pyqt_table(self._roiToAdd, col_names, cols)
        self._fcn_reset_roi_list()

    def _fcn_reset_roi_list(self):
        """Reset ROIs selection."""
        # Unchecked all ROIs :
        for num in range(self._roiToAdd.rowCount()):
            c = QtWidgets.QTableWidgetItem()
            c.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            c.setCheckState(QtCore.Qt.Unchecked)
            self._roiToAdd.setItem(num, 0, c)

    def _fcn_get_selected_rois(self):
        """Get the list of selected ROIs."""
        _roiToAdd = []
        all_idx = list(self.roi.get_labels()['index'])
        for num in range(self._roiToAdd.rowCount()):
            item = self._roiToAdd.item(num, 0)
            if item.checkState():
                _roiToAdd.append(all_idx[num])
        return _roiToAdd

    def _fcn_set_selected_rois(self, selection):
        """Set a list of selected rois."""
        for k in selection:
            item = self._roiToAdd.item(k)
            item.setCheckState(QtCore.Qt.Checked)

    def _fcn_apply_roi_selection(self, _, roi_name='roi'):
        """Apply ROI selection."""
        # Get the list of selected ROIs :
        _roiToAdd = self._fcn_get_selected_rois()
        smooth = self._roiSmooth.value()

        if _roiToAdd:
            self.roi.select_roi(_roiToAdd, smooth=smooth)
            self.roi.camera = self._camera
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
        self.roi.mesh.translucent = self._roiTransp.isChecked()

    ###########################################################################
    ###########################################################################
    #                            CROSS-SECTIONS
    ###########################################################################
    ###########################################################################
    def _fcn_crossec_sl_limits(self):
        """Define (min, max) of sliders."""
        # Sagittal / Coronal / Axial :
        self._csSagit.setMaximum(self.cross_sec._vol.shape[0] - 1)
        self._csCoron.setMaximum(self.cross_sec._vol.shape[1] - 1)
        self._csAxial.setMaximum(self.cross_sec._vol.shape[2] - 1)

    def _fcn_crossec_move(self, *args, update=False):
        """Trigged when a slider move."""
        # Get center position :
        dx = min(max(0, self._csSagit.value()), self.cross_sec._vol.shape[0])
        dy = min(max(0, self._csCoron.value()), self.cross_sec._vol.shape[1])
        dz = min(max(0, self._csAxial.value()), self.cross_sec._vol.shape[2])
        # Get selected colormap :
        cmap = str(self._csCmap.currentText())
        self.cross_sec.set_data((dx, dy, dz), cmap=cmap, update=update)

    def _fcn_crossec_cmap(self):
        """Change cross-sections colormap."""
        self._fcn_crossec_move(update=True)

    def _fcn_crossec_viz(self):
        """Control cross-sections visibility."""
        self.menuDispCrossec.setChecked(self._sec_grp.isChecked())
        self._fcn_menu_disp_crossec()

    def _fcn_crossec_change(self):
        """Change the cross-sections subdivision type."""
        # Get selected volume :
        name = str(self._csDiv.currentText())
        # Select the volume :
        self.cross_sec(name)
        # Update clim and minmax :
        self._fcn_crossec_sl_limits()
        self._fcn_crossec_move(update=True)

    ###########################################################################
    ###########################################################################
    #                                 VOLUME
    ###########################################################################
    ###########################################################################
    def _fcn_vol_visible(self):
        """Display or hide ROI."""
        self.menuDispVol.setChecked(self._vol_grp.isChecked())
        self._fcn_menu_disp_vol()

    def _fcn_vol_change(self):
        """Change volume."""
        # Get selected volume :
        name = str(self._volDiv.currentText())
        if self.volume.name != name:
            self.volume(name)

    def _fcn_vol_rendering(self):
        """Change rendering method."""
        method = str(self._volRendering.currentText())
        self._volIsoTh.setEnabled(method == 'iso')
        self.volume.method = method

    def _fcn_vol_cmap(self):
        """Change volume colormap."""
        self.volume.cmap = str(self._volCmap.currentText())

    def _fcn_vol_threshold(self):
        """Change volume threshold."""
        self.volume.threshold = float(self._volIsoTh.value())
