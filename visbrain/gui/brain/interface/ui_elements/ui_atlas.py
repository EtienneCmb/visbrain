"""Top level class for managing the MNI (rotation, structure...).

Make the bridge between GUI and deep functions. Add some usefull
commands for the user
"""
import numpy as np
import logging
from PyQt5 import QtCore

from visbrain.objects.volume_obj import VOLUME_CMAPS
from visbrain.utils import fill_pyqt_table


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
        # Slices :
        self._fcn_brain_reset_slider()
        self._brain_xmin.valueChanged.connect(self._fcn_brain_slices)
        self._brain_xmax.valueChanged.connect(self._fcn_brain_slices)
        self._brain_ymin.valueChanged.connect(self._fcn_brain_slices)
        self._brain_ymax.valueChanged.connect(self._fcn_brain_slices)
        self._brain_zmin.valueChanged.connect(self._fcn_brain_slices)
        self._brain_zmax.valueChanged.connect(self._fcn_brain_slices)
        # Light :
        self._brain_inlight.clicked.connect(self._fcn_brain_inlight)

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
        # Roi smooth :
        self._roiIsSmooth.clicked.connect(self._fcn_roi_smooth)
        self._roiSmooth.setEnabled(False)
        # MIST level :
        self._roiLevel.setEnabled('mist' in self.roi.name.lower())
        self._roiLevel.currentIndexChanged.connect(self._fcn_build_roi_list)
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
        self._csSagit.setValue(self.cross_sec._bgd._sagittal)
        self._csCoron.setValue(self.cross_sec._bgd._coronal)
        self._csAxial.setValue(self.cross_sec._bgd._axial)
        self._csSagit.sliderMoved.connect(self._fcn_crossec_move)
        self._csCoron.sliderMoved.connect(self._fcn_crossec_move)
        self._csAxial.sliderMoved.connect(self._fcn_crossec_move)
        # Subdivision :
        self._csDiv.addItems(vol_list)
        self._csDiv.currentIndexChanged.connect(self._fcn_crossec_change)
        self._csLevel.currentIndexChanged.connect(self._fcn_crossec_change)
        self._csInterp.currentIndexChanged.connect(self._fcn_crossec_interp)
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
        if self.atlas.name != template:
            self.atlas.set_data(name=template, hemisphere=hemisphere)
            self.atlas.scale = self._gl_scale
            self.atlas.reset_camera()
            self.atlas.rotate('top')
            self.atlas._name = template
        if self.atlas.hemisphere != hemisphere:
            self.atlas.hemisphere = hemisphere
        self._fcn_brain_reset_slider()

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

    def _fcn_brain_reset_slider(self):
        """Reset min/max slice sliders."""
        v = self.atlas.vertices
        n_cut = 1000
        xmin, xmax = v[:, 0].min() - 1., v[:, 0].max() + 1.
        ymin, ymax = v[:, 1].min() - 1., v[:, 1].max() + 1.
        zmin, zmax = v[:, 2].min() - 1., v[:, 2].max() + 1.
        # xmin
        self._brain_xmin.setMinimum(xmin)
        self._brain_xmin.setMaximum(xmax)
        self._brain_xmin.setSingleStep((xmin - xmax) / n_cut)
        self._brain_xmin.setValue(xmin)
        # xmax
        self._brain_xmax.setMinimum(xmin)
        self._brain_xmax.setMaximum(xmax)
        self._brain_xmax.setSingleStep((xmin - xmax) / n_cut)
        self._brain_xmax.setValue(xmax)
        # ymin
        self._brain_ymin.setMinimum(ymin)
        self._brain_ymin.setMaximum(ymax)
        self._brain_ymin.setSingleStep((ymin - ymax) / n_cut)
        self._brain_ymin.setValue(ymin)
        # ymax
        self._brain_ymax.setMinimum(ymin)
        self._brain_ymax.setMaximum(ymax)
        self._brain_ymax.setSingleStep((ymin - ymax) / n_cut)
        self._brain_ymax.setValue(ymax)
        # zmin
        self._brain_zmin.setMinimum(zmin)
        self._brain_zmin.setMaximum(zmax)
        self._brain_zmin.setSingleStep((zmin - zmax) / n_cut)
        self._brain_zmin.setValue(zmin)
        # zmax
        self._brain_zmax.setMinimum(zmin)
        self._brain_zmax.setMaximum(zmax)
        self._brain_zmax.setSingleStep((zmin - zmax) / n_cut)
        self._brain_zmax.setValue(zmax)

    def _fcn_brain_slices(self):
        """Slice the brain."""
        self.atlas.mesh.xmin = float(self._brain_xmin.value())
        self.atlas.mesh.xmax = float(self._brain_xmax.value())
        self.atlas.mesh.ymin = float(self._brain_ymin.value())
        self.atlas.mesh.ymax = float(self._brain_ymax.value())
        self.atlas.mesh.zmin = float(self._brain_zmin.value())
        self.atlas.mesh.zmax = float(self._brain_zmax.value())
        self.atlas.mesh.update()

    def _fcn_brain_inlight(self):
        """Set light to be inside the brain."""
        self.atlas.mesh.inv_light = self._brain_inlight.isChecked()
        self.atlas.mesh.update()

    ###########################################################################
    ###########################################################################
    #                          REGION OF INTEREST
    ###########################################################################
    ###########################################################################
    def _fcn_roi_visible(self):
        """Display or hide ROI."""
        self.menuDispROI.setChecked(self._roi_grp.isChecked())
        self._fcn_menu_disp_roi()

    def _fcn_roi_smooth(self):
        """Enable ROI smoothing."""
        self._roiSmooth.setEnabled(self._roiIsSmooth.isChecked())

    def _fcn_build_roi_list(self):
        """Build a list of checkable ROIs."""
        # Select volume :
        selected_roi = str(self._roiDiv.currentText())
        # Mist :
        if 'mist' in selected_roi.lower():
            self._roiLevel.setEnabled('mist' in selected_roi)
            level = str(self._roiLevel.currentText())
            selected_roi += '_%s' % level
        if self.roi.name != selected_roi:
            self.roi(selected_roi)
        # Clear widget list and add ROIs :
        self._roiToAdd.reset()
        df = self.roi.get_labels()
        if 'mist' in selected_roi.lower():
            df = df[['index', 'name_%s' % level]]
        col_names = list(df.keys())
        col_names.pop(col_names.index('index'))
        cols = [list(df[k]) for k in col_names if k not in ['', 'index']]
        # Build the table with the filter :
        self._roiModel = fill_pyqt_table(self._roiToAdd, col_names, cols,
                                         filter=self._roiFilter, check=0,
                                         filter_col=0)
        # By default, uncheck items :
        self._fcn_reset_roi_list()

    def _fcn_reset_roi_list(self):
        """Reset ROIs selection."""
        # Unchecked all ROIs :
        for num in range(self._roiModel.rowCount()):
            self._roiModel.item(num, 0).setCheckState(QtCore.Qt.Unchecked)

    def _fcn_get_selected_rois(self):
        """Get the list of selected ROIs."""
        _roiToAdd = []
        all_idx = list(self.roi.get_labels()['index'])
        for num in range(self._roiModel.rowCount()):
            item = self._roiModel.item(num, 0)
            if item.checkState():
                _roiToAdd.append(all_idx[num])
        return _roiToAdd

    def _fcn_apply_roi_selection(self, _, roi_name='roi'):
        """Apply ROI selection."""
        # Get the list of selected ROIs :
        _roiToAdd = self._fcn_get_selected_rois()
        smooth = self._roiSmooth.value() * int(self._roiIsSmooth.isChecked())
        uni_col = bool(self._roiUniColor.isChecked())

        if _roiToAdd:
            self.roi.select_roi(_roiToAdd, smooth=smooth, unique_color=uni_col)
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
        sl = self.cross_sec.slice_to_pos((dx, dy, dz))
        self.cross_sec.cut_coords(sl)

    def _fcn_crossec_viz(self):
        """Control cross-sections visibility."""
        self.menuDispCrossec.setChecked(self._sec_grp.isChecked())
        self._fcn_menu_disp_crossec()

    def _fcn_crossec_change(self):
        """Change the cross-sections subdivision type."""
        # Get selected volume :
        name = str(self._csDiv.currentText())
        level = str(self._csLevel.currentText())
        is_mist = name == 'mist'
        self._csLevel.setEnabled(is_mist)
        name = name + '_' + level if is_mist else name
        # Select the volume :
        self.cross_sec(name)
        self.cross_sec.contrast = 0.
        # Update clim and minmax :
        self._fcn_crossec_sl_limits()
        self._fcn_crossec_interp()
        # self.cross_sec.cut_coords(None)
        self._fcn_crossec_move()
        self.cross_sec._set_text(0, 'File = ' + name)
        # Reset sliders :
        self._csSagit.setValue(self.cross_sec._sagittal)
        self._csCoron.setValue(self.cross_sec._coronal)
        self._csAxial.setValue(self.cross_sec._axial)

    def _fcn_crossec_interp(self):
        """Interpolation method."""
        self.cross_sec.interpolation = str(self._csInterp.currentText())

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
