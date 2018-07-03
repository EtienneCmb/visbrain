"""GUI interactions with the contextual menu."""
import vispy.scene.cameras as viscam

from ....utils import HelpMenu


class UiMenu(HelpMenu):
    """Interactions with the menu."""

    def __init__(self):
        """Init."""
        base = 'http://visbrain.org/brain.html'
        sections = {'Brain': base}
        HelpMenu.__init__(self, sections)
        # =============================================================
        # FILE
        # =============================================================
        # ----------- SAVE -----------
        # Screenshots :
        self.menuScreenshot.triggered.connect(self._fcn_show_screenshot)
        # Config :
        self.menuSaveGuiConfig.triggered.connect(self._fcn_save_config)
        # ----------- LOAD -----------
        # Config :
        self.menuLoadGuiConfig.triggered.connect(self._fcn_load_config)
        # Exit :
        self.actionExit.triggered.connect(self.closeEvent)

        # =============================================================
        # DISPLAY
        # =============================================================
        # Quick settings panel :
        self.menuDispQuickSettings.triggered.connect(self._fcn_menu_disp_set)
        # Brain :
        self.menuDispBrain.triggered.connect(self._fcn_menu_disp_brain)
        # Cross-sections :
        self.menuDispCrossec.triggered.connect(self._fcn_menu_disp_crossec)
        # Volume :
        self.menuDispVol.triggered.connect(self._fcn_menu_disp_vol)
        # Sources :
        self.menuDispSources.triggered.connect(self._fcn_menu_disp_sources)
        # Connectivity :
        self.menuDispConnect.triggered.connect(self._fcn_menu_disp_connect)
        # ROI :
        self.menuDispROI.triggered.connect(self._fcn_menu_disp_roi)
        # Colorbar :
        self.menuDispCbar.triggered.connect(self._fcn_menu_disp_cbar)

        # =============================================================
        # ROTATION
        # =============================================================
        self.menuRotTop.triggered.connect(self._fcn_rotate_top)
        self.menuRotBottom.triggered.connect(self._fcn_rotate_bottom)
        self.menuRotLeft.triggered.connect(self._fcn_rotate_left)
        self.menuRotRight.triggered.connect(self._fcn_rotate_right)
        self.menuRotFront.triggered.connect(self._fcn_rotate_front)
        self.menuRotBack.triggered.connect(self._fcn_rotate_back)

        # =============================================================
        # CAMERA
        # =============================================================
        self.menuCamFly.triggered.connect(self._fcn_set_cam_fly)

        # =============================================================
        # PROJECTIONS
        # =============================================================
        self.menuCortProj.triggered.connect(self._fcn_menu_projection)
        self.menuCortRep.triggered.connect(self._fcn_menu_repartition)

    def _fcn_show_screenshot(self):
        """Display the screenshot GUI."""
        self.show_gui_screenshot()

    ###########################################################################
    #                                DISPLAY
    ###########################################################################
    def _fcn_menu_disp_set(self):
        """Toggle method for display / hide the settings panel."""
        viz = self.menuDispQuickSettings.isChecked()
        self.q_widget.setVisible(viz)

    def _fcn_menu_disp_brain(self):
        """Display/hide the main Brain."""
        viz = self.menuDispBrain.isChecked()
        self._brain_grp.setChecked(viz)
        self.atlas.visible_obj = viz
        self._fcn_menu_set_object(0)

    def _fcn_menu_disp_roi(self):
        """Display/hide ROI."""
        viz = self.menuDispROI.isChecked()
        self.roi.visible_obj = viz
        self._roi_grp.setChecked(viz)
        self._fcn_menu_set_object(1)

    def _fcn_menu_disp_vol(self):
        """Display/hide the volume."""
        viz = self.menuDispVol.isChecked()
        # Set volume visible/hide :
        self.volume.visible_obj = viz
        self._vol_grp.setChecked(viz)
        self._fcn_menu_set_object(2)

    def _fcn_menu_disp_crossec(self):
        """Display/hide the Cross-sections."""
        viz = self.menuDispCrossec.isChecked()
        # Set cross-sections visible/hide :
        self._sec_grp.setChecked(viz)
        self.cross_sec.visible_obj = viz
        # Disable split view if not visible :
        self._objsPage.setCurrentIndex(int(viz))
        self._fcn_crossec_sl_limits()
        self._fcn_menu_set_object(3)

    def _fcn_menu_disp_sources(self):
        """Display/hide sources."""
        viz = self.menuDispSources.isChecked()
        self.sources.visible_obj = viz
        self._s_grp.setChecked(viz)
        self._fcn_menu_set_object(4)

    def _fcn_menu_disp_connect(self):
        """Display/hide connectivity."""
        viz = self.menuDispConnect.isChecked()
        self.connect.visible_obj = viz
        self._c_grp.setChecked(viz)
        self._fcn_menu_set_object(5)

    def _fcn_menu_disp_cbar(self):
        """Display/hide the colorbar."""
        viz = self.menuDispCbar.isChecked()
        self.cbqt.cbui._cbar_grp.setChecked(viz)
        self.cbpanelW.setVisible(viz)

    def _fcn_menu_set_object(self, nb):
        """Select object in the list."""
        need_change = self._obj_type_lst.currentIndex() == nb
        if self._obj_type_lst.model().item(nb).isEnabled() and not need_change:
            self._obj_type_lst.setCurrentIndex(nb)

    ###########################################################################
    #                                ROTATION
    ###########################################################################
    def _fcn_rotate_top(self):
        """Display top scene."""
        self.atlas.rotate('top')

    def _fcn_rotate_bottom(self):
        """Display bottom scene."""
        self.atlas.rotate('bottom')

    def _fcn_rotate_left(self):
        """Display left scene."""
        self.atlas.rotate('left')

    def _fcn_rotate_right(self):
        """Display ritgh scene."""
        self.atlas.rotate('right')

    def _fcn_rotate_front(self):
        """Display front scene."""
        self.atlas.rotate('front')

    def _fcn_rotate_back(self):
        """Display back scene."""
        self.atlas.rotate('back')

    ###########################################################################
    #                                CAMERA
    ###########################################################################
    def _fcn_set_cam_fly(self):
        """Switch between different types of cameras.

        The user can either use a Turntable or a Fly camera. The turntable
        camera is centered on the central object. Every rotation is arround
        this object. The fly camera can be used for go in every deep part of
        the brain (not easy to control).
        """
        # Get radio buttons values :
        if self.menuCamFly.isChecked():
            # camera = viscam.PanZoomCamera(aspect=1)
            camera = viscam.FlyCamera(name='fly')
        else:
            camera = viscam.TurntableCamera(azimuth=0, distance=1000,
                                            name='turntable')

        # Add camera to the mesh and to the canvas :
        self.view.wc.camera = camera
        self.atlas.mesh.set_camera(camera)
        self.roi.camera = camera
        self.view.wc.update()
        if camera.name == 'turntable':
            self.atlas.rotate(fixed='axial_0')

    ###########################################################################
    #                           PROJECTIONS
    ###########################################################################
    def _fcn_menu_projection(self):
        """Run the cortical projection."""
        self._s_proj_type.setCurrentIndex(0)
        self._fcn_source_proj('')

    def _fcn_menu_repartition(self):
        """Run the cortical projection."""
        self._s_proj_type.setCurrentIndex(1)
        self._fcn_source_proj('')
