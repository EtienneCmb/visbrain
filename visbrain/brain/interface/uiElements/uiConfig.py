"""Enable the user to save/load the Brain config in a json file."""
from warnings import warn
from ....io import dialogLoad, dialogSave
from ....utils import color2json

__all__ = ["uiConfig"]


class uiConfig(object):
    """Main class for saving/loading the configuration."""

    ###########################################################################
    ###########################################################################
    #                                   SAVE
    ###########################################################################
    ###########################################################################
    def _fcn_saveConfig(self, _, filename=None):
        """Save the configuration."""
        import json
        # Get the name of the file to be saved :
        if filename is None:
            filename = dialogSave(self, 'Save config File', 'config',
                                  "Text file (*.txt);;All files (*.*)")
        if filename:
            with open(filename, 'w') as f:
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
                rect = self.view.cbwc.camera.rect
                config['CamCbState'] = list(rect.pos) + list(rect.size)
                # ----------------- GUI SETTINGS -----------------
                # Background color :
                bgd = (self.bgd_red.value(), self.bgd_green.value(),
                       self.bgd_blue.value())
                config['BcgColor'] = bgd
                # Tab :
                config['CurrentTab'] = self.QuickSettings.currentIndex()
                # ----------------- BRAIN -----------------
                config['BrainTransp'] = self._brainTransp.isChecked()
                config['BrainHemi'] = self._brainPickHemi.currentIndex()
                config['BrainTemplate'] = self._brainTemplate.currentIndex()
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
                config['StextShow'] = self.q_stextshow.isChecked()
                config['StextSz'] = self.q_stextsize.value()
                config['StextCol'] = color2json(self.q_stextcolor)
                config['StextXYZ'] = (self.x_text.value(), self.y_text.value(),
                                      self.z_text.value())
                # Source's projection settings :
                config['SprojRad'] = self._uitRadius.value()
                config['SprojType'] = self._uitPickProj.currentIndex()
                config['SprojOn'] = self._uitProjectOn.currentIndex()
                config['SprojCon'] = self._uitContribute.isChecked()
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
                # ----------------- ROI -----------------
                config['RoiTransp'] = self._roiTransp.isChecked()
                config['RoiAnat'] = self._roiSubdivision.currentIndex()
                config['RoiSmooth'] = self._roiSmooth.value()
                struct2add = [str(k) for k in self._struct2add]
                config['RoiStruct'] = struct2add
                # ----------------- CBAR -----------------
                # Visual:
                dico = self.cb.colorbarW.to_dict()
                del dico["bgcolor"]  # Don't to save the background color
                config['CbarVisual'] = dico

                json.dump(config, f)

    ###########################################################################
    ###########################################################################
    #                                   LOAD
    ###########################################################################
    ###########################################################################
    def _fcn_loadConfig(self, _, filename=None):
        """Load the configuration."""
        import json
        if not filename:
            filename = dialogLoad(self, 'Load config File', 'config',
                                  "Text file (*.txt);;All files (*.*)")
        if filename:
            with open(filename) as f:
                # Load the configuration file :
                config = json.load(f)

                def _try(string, self=self, config=config):
                    """Execute the string.

                    This function insure backward compatibility for loading the
                    configuration file.
                    """
                    try:
                        exec(string)
                    except:
                        warn("Cannot execute for loading the config : "+string)

                # ----------------- VISIBLE OBJECTS -----------------
                # Settings :
                _try("self.menuDispQuickSettings.setChecked("
                     "config['SettingViz'])")
                _try("self._fcn_menuDispSet()")
                # Brain :
                _try("self.menuDispBrain.setChecked(config['BrainViz'])")
                _try("self._fcn_menuBrain()")
                # Sources
                _try("self.menuDispSources.setChecked(config['SourcesViz'])")
                _try("self._fcn_menuSources()")
                # Connect :
                _try("self.menuDispConnect.setChecked(config['ConnectViz'])")
                _try("self._fcn_menuConnect()")
                # ROI :
                _try("self.menuDispROI.setChecked(config['ROIViz'])")
                _try("self._fcn_menuROI()")
                # Cbar :
                _try("self.menuDispCbar.setChecked(config['CbarViz'])")
                _try("self._fcn_menuCbar()")
                # ----------------- CAMERA -----------------
                _try("self.view.wc.camera.set_state(config['CamState'])")
                _try("self.view.cbwc.camera.rect=config['CamCbState']")
                # ----------------- BRAIN -----------------
                _try("self._brainTransp.setChecked(config['BrainTransp'])")
                _try("self._brainPickHemi.setCurrentIndex(config["
                     "'BrainHemi'])")
                _try("self._brainTemplate.setCurrentIndex(config["
                     "'BrainTemplate'])")
                _try("self._brain_control('')")
                _try("self._light_reflection()")
                # ----------------- SOURCES -----------------
                # Sources object :
                _try("self._sourcesPickdisp.setCurrentIndex(config["
                     "'SourcesDisp'])")
                _try("self._fcn_sourcesDisplay()")
                _try("self.s_Symbol.setCurrentIndex(config['SourcesSym'])")
                _try("self.s_EdgeColor.setText(str(config['SourcesEcol']))")
                _try("self.s_EdgeWidth.setValue(config['SourcesEw'])")
                _try("self._fcn_MarkerLook()")
                _try("self.s_radiusMin.setValue(config['SourcesRm'])")
                _try("self.s_radiusMax.setValue(config['SourcesRM'])")
                _try("self.s_Scaling.setChecked(config['SourcesScale'])")
                _try("self._fcn_MarkerRadius()")
                # Source's text :
                _try("self.q_stextshow.setChecked(config['StextShow'])")
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
                # ----------------- ROI -----------------
                _try("self._roiTransp.setChecked(config['RoiTransp'])")
                _try("self._roiSubdivision.setCurrentIndex(config['RoiAnat'])")
                _try("self._roiSmooth.setValue(config['RoiSmooth'])")
                _try("self.struct2add.clear()")
                _try("self._struct2add = config['RoiStruct']")
                _try("self._fcn_update_list()")
                # ----------------- GUI SETTINGS -----------------
                # Background color :
                rgb = config['BcgColor']
                _try("self.bgd_red.setValue("+str(rgb[0])+")")
                _try("self.bgd_green.setValue("+str(rgb[1])+")")
                _try("self.bgd_blue.setValue("+str(rgb[2])+")")
                _try("self._fcn_bgd_color()")
                # Tab :
                _try("self.QuickSettings.setCurrentIndex(config["
                     "'CurrentTab'])")
                # ----------------- CBAR -----------------
                # Cbar visual :
                _try("self.cb.colorbarW.from_dict(config['CbarVisual'])")
