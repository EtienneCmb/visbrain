"""Enable the user to save/load the Brain config in a json file."""
from warnings import warn

from visbrain.io import (dialog_load, dialog_save, save_config_json,
                         load_config_json)
from visbrain.utils import color2json


class UiConfig(object):
    """Main class for saving/loading the configuration."""

    ###########################################################################
    ###########################################################################
    #                                   SAVE
    ###########################################################################
    ###########################################################################
    def _fcn_save_config(self, _, filename=None):
        """Save the configuration."""
        # Get the name of the file to be saved :
        if filename is None:
            filename = dialog_save(self, 'Save config File', 'config',
                                   "Text file (*.txt);;All files (*.*)")
        if filename:
            config = {}

            # ----------------- VISIBLE OBJECTS -----------------
            config['SettingViz'] = self.menuDispQuickSettings.isChecked()
            config['BrainViz'] = self.menuDispBrain.isChecked()
            config['SourcesViz'] = self.menuDispSources.isChecked()
            config['ConnectViz'] = self.menuDispConnect.isChecked()
            config['ROIViz'] = self.menuDispROI.isChecked()
            config['CbarViz'] = self.menuDispCbar.isChecked()

            # ----------------- CAMERAS -----------------
            config['CamState'] = self.view.wc.camera.get_state()
            rect = self.cbqt.cbviz._wc.camera.rect
            config['CamCbState'] = list(rect.pos) + list(rect.size)

            # ----------------- GUI SETTINGS -----------------
            # Background color :
            bgd = (self.bgd_red.value(), self.bgd_green.value(),
                   self.bgd_blue.value())
            config['BcgColor'] = bgd
            # Tab :
            config['CurrentTab'] = self.QuickSettings.currentIndex()

            # ----------------- BRAIN -----------------
            # Brain :
            config['BrainTransp'] = self._brain_translucent.isChecked()
            config['BrainHemi'] = self._brainPickHemi.currentIndex()
            config['BrainTemplate'] = self._brainTemplate.currentIndex()
            # ROI :
            config['RoiTransp'] = self._roiTransp.isChecked()
            config['RoiAnat'] = self._roiDiv.currentIndex()
            config['RoiSmooth'] = self._roiSmooth.value()
            config['RoiStruct'] = self._fcn_get_selected_rois()
            # Cross-sections :
            config['CsSagit'] = self._csSagit.value()
            config['CsCoron'] = self._csCoron.value()
            config['CsAxial'] = self._csAxial.value()
            config['CsDiv'] = self._csDiv.currentIndex()
            config['CsCmap'] = self._csCmap.currentIndex()
            config['CsTransp'] = self._csTransp.isChecked()
            config['CsSplit'] = self._csSplit.isChecked()
            config['CsGrp'] = self.grpSec.isChecked()
            # Volume :
            config['VolDiv'] = self._volDiv.currentIndex()
            config['VolRendering'] = self._volRendering.currentIndex()
            config['VolCmap'] = self._volCmap.currentIndex()
            config['VolTh'] = self._volIsoTh.value()
            config['VolGrp'] = self.grpVol.isChecked()

            # ----------------- SOURCES -----------------
            # Sources object :
            config['SourcesDisp'] = self._sourcesPickdisp.currentIndex()
            config['SourcesSym'] = self.s_Symbol.currentIndex()
            config['SourcesRm'] = self.s_radiusMin.value()
            config['SourcesRM'] = self.s_radiusMax.value()
            config['SourcesEcol'] = color2json(self.s_EdgeColor, False)
            config['SourcesEw'] = self.s_EdgeWidth.value()
            config['SourcesScale'] = self.s_Scaling.isChecked()
            # Source's text :
            config['StextShow'] = self.grpText.isChecked()
            config['StextSz'] = self.q_stextsize.value()
            config['StextCol'] = color2json(self.q_stextcolor)
            config['StextXYZ'] = (self.x_text.value(), self.y_text.value(),
                                  self.z_text.value())
            # Source's projection settings :
            config['SprojRad'] = self._uitRadius.value()
            config['SprojType'] = self._uitPickProj.currentIndex()
            config['SprojOn'] = self._uitProjectOn.currentIndex()
            config['SprojCon'] = self._uitContribute.isChecked()
            # Source's time-series :
            config['StsWidth'] = self._tsWidth.value()
            config['StsAmp'] = self._tsAmp.value()
            config['StsLw'] = self._tsLw.value()
            config['StsDxyz'] = (self._tsDx.value(), self._tsDy.value(),
                                 self._tsDz.value())
            config['StsColor'] = color2json(self._tsColor)

            # ----------------- CONNECTIVITY -----------------
            config['ConnectCby'] = self.uiConnect_colorby.currentIndex()
            config['ConnectAlp'] = self._connectStaDynTransp.currentIndex()
            config['ConnectMin'] = self.uiConnect_dynMin.value()
            config['ConnectMax'] = self.uiConnect_dynMax.value()
            config['ConnectRad'] = self._densityRadius.value()
            config['ConnectLw'] = self.uiConnect_lw.value()
            config['ConnectBun'] = self._conBlEnable.isChecked()
            config['ConnectBunRad'] = self._conBlRadius.value()
            config['ConnectBunDxyz'] = self._conBlDxyz.value()

            # ----------------- CBAR -----------------
            # Visual:
            config['Cbar'] = self.cbqt.cbobjs.to_dict(alldicts=True)
            config['CbarIdx'] = self.cbqt.cbui.object.currentIndex()

            # Write the configuration into a json file :
            save_config_json(filename, config)

    ###########################################################################
    ###########################################################################
    #                                   LOAD
    ###########################################################################
    ###########################################################################
    def _fcn_load_config(self, _, filename=None):
        """Load the configuration."""
        if not filename:
            filename = dialog_load(self, 'Load config File', 'config',
                                   "Text file (*.txt);;All files (*.*)")
        if filename:
            config = load_config_json(filename)

            def _try(string, self=self, config=config):
                """Execute the string.

                This function insure backward compatibility for loading the
                configuration file.
                """
                try:
                    exec(string)
                except:
                    warn("Cannot execute for loading the config : " + string)

            # ----------------- VISIBLE OBJECTS -----------------
            # Settings :
            _try("self.menuDispQuickSettings.setChecked("
                 "config['SettingViz'])")
            _try("self._fcn_menu_disp_set()")
            # Brain :
            _try("self.menuDispBrain.setChecked(config['BrainViz'])")
            _try("self._fcn_menu_disp_brain()")
            # Sources
            _try("self.menuDispSources.setChecked(config['SourcesViz'])")
            _try("self._fcn_menu_disp_sources()")
            # Connect :
            _try("self.menuDispConnect.setChecked(config['ConnectViz'])")
            _try("self._fcn_menu_disp_connect()")
            # ROI :
            _try("self.menuDispROI.setChecked(config['ROIViz'])")
            _try("self._fcn_menu_disp_roi()")
            # Cbar :
            _try("self.menuDispCbar.setChecked(config['CbarViz'])")
            _try("self._fcn_menu_disp_cbar()")

            # ----------------- CAMERA -----------------
            _try("self.view.wc.camera.set_state(config['CamState'])")
            _try("self.cbqt.cbviz._wc.camera.rect=config['CamCbState']")

            # ----------------- BRAIN -----------------
            # Brain :
            _try("self._brain_translucent.setChecked(config['BrainTransp'])")
            _try("self._brainPickHemi.setCurrentIndex(config["
                 "'BrainHemi'])")
            _try("self._brainTemplate.setCurrentIndex(config["
                 "'BrainTemplate'])")
            _try("self._brain_control()")
            _try("self._light_reflection()")
            # ROIs :
            _try("self._roiTransp.setChecked(config['RoiTransp'])")
            _try("self._roiDiv.setCurrentIndex(config['RoiAnat'])")
            _try("self._roiSmooth.setValue(config['RoiSmooth'])")
            _try("self._roiToAdd.clear()")
            _try("self._fcn_build_roi_list()")
            _try("self._fcn_set_selected_rois(config['RoiStruct'])")
            _try("self._fcn_update_list()")
            # Cross-sections :
            _try("self._csSagit.setValue(config['CsSagit'])")
            _try("self._csCoron.setValue(config['CsCoron'])")
            _try("self._csAxial.setValue(config['CsAxial'])")
            _try("self._csDiv.setCurrentIndex(config['CsDiv'])")
            _try("self._csCmap.setCurrentIndex(config['CsCmap'])")
            _try("self._csTransp.setChecked(config['CsTransp'])")
            _try("self._csSplit.setChecked(config['CsSplit'])")
            _try("self.grpSec.setChecked(config['CsGrp'])")
            _try("self._fcn_crossec_change()")
            _try("self._fcn_crossec_split()")
            # Volume :
            _try("self._volDiv.setCurrentIndex(config['VolDiv'])")
            _try("self._volRendering.setCurrentIndex(config['VolRendering'])")
            _try("self._volCmap.setCurrentIndex(config['VolCmap'])")
            _try("self._volIsoTh.setValue(config['VolTh'])")
            _try("self.grpVol.setChecked(config['VolGrp'])")
            _try("self._fcn_vol_change()")

            # ----------------- SOURCES -----------------
            # Sources object :
            _try("self._sourcesPickdisp.setCurrentIndex(config["
                 "'SourcesDisp'])")
            _try("self._fcn_sources_display()")
            _try("self.s_Symbol.setCurrentIndex(config['SourcesSym'])")
            _try("self.s_EdgeColor.setText(str(config['SourcesEcol']))")
            _try("self.s_EdgeWidth.setValue(config['SourcesEw'])")
            _try("self._fcn_sources_look()")
            _try("self.s_radiusMin.setValue(config['SourcesRm'])")
            _try("self.s_radiusMax.setValue(config['SourcesRM'])")
            _try("self.s_Scaling.setChecked(config['SourcesScale'])")
            _try("self._fcn_sources_radius()")
            # Source's text :
            _try("self.grpText.setChecked(config['StextShow'])")
            _try("self.q_stextsize.setValue(config['StextSz'])")
            _try("self.q_stextcolor.setText(str(config['StextCol']))")
            _try("self.x_text.setValue(config['StextXYZ'][0])")
            _try("self.y_text.setValue(config['StextXYZ'][1])")
            _try("self.z_text.setValue(config['StextXYZ'][2])")
            # Source's projection settings :
            _try("self._uitRadius.setValue(config['SprojRad'])")
            _try("self._uitPickProj.setCurrentIndex(config['SprojType'])")
            _try("self._uitProjectOn.setCurrentIndex(config['SprojOn'])")
            _try("self._uitContribute.setChecked(config['SprojCon'])")
            # Source's time-series :
            _try("self._tsWidth.setValue(config['StsWidth'])")
            _try("self._tsAmp.setValue(config['StsAmp'])")
            _try("self._tsLw.setValue(config['StsLw'])")
            _try("self._tsDx.setValue(config['StsDxyz'][0])")
            _try("self._tsDy.setValue(config['StsDxyz'][1])")
            _try("self._tsDz.setValue(config['StsDxyz'][2])")
            _try("self._tsColor.setText(str(config['StsColor']))")
            _try("self._fcn_ts_update()")

            # ----------------- CONNECTIVITY -----------------
            _try("self.uiConnect_colorby.setCurrentIndex(config["
                 "'ConnectCby'])")
            _try("self._connectStaDynTransp.setCurrentIndex(config["
                 "'ConnectAlp'])")
            _try("self.uiConnect_dynMin.setValue(config['ConnectMin'])")
            _try("self.uiConnect_dynMax.setValue(config['ConnectMax'])")
            _try("self._densityRadius.setValue(config['ConnectRad'])")
            _try("self.uiConnect_lw.setValue(config['ConnectLw'])")
            _try("self._conBlEnable.setChecked(config['ConnectBun'])")
            _try("self._conBlRadius.setValue(config['ConnectBunRad'])")
            _try("self._conBlDxyz.setValue(config['ConnectBunDxyz'])")

            # ----------------- GUI SETTINGS -----------------
            # Background color :
            rgb = config['BcgColor']
            _try("self.bgd_red.setValue(" + str(rgb[0]) + ")")
            _try("self.bgd_green.setValue(" + str(rgb[1]) + ")")
            _try("self.bgd_blue.setValue(" + str(rgb[2]) + ")")
            _try("self._fcn_bgd_color()")
            # Tab :
            _try("self.QuickSettings.setCurrentIndex(config["
                 "'CurrentTab'])")

            # ----------------- CBAR -----------------
            # Cbar visual :
            _try("self.cbqt.cbobjs.from_dict(config['Cbar'])")
            _try("self.cbqt._disconnect()")
            _try("self.cbqt._initialize()")
            _try("self.cbqt._connect()")
            _try("self.cbqt.link('Projection', self._fcn_link_proj, "
                 "self._fcn_minmax_proj)")
            _try("self.cbqt.link('Connectivity', self._fcn_link_connect, "
                 "self._fcn_minmax_connect)")
