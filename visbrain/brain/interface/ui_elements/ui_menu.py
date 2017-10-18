"""GUI interactions with the contextual menu."""
from PyQt5 import QtWidgets
import vispy.scene.cameras as viscam

from ....utils import toggle_enable_tab, HelpMenu


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
        self.menuSaveGuiConfig.triggered.connect(self._fcn_saveConfig)
        # ----------- LOAD -----------
        # Config :
        self.menuLoadGuiConfig.triggered.connect(self._fcn_loadConfig)
        # Exit :
        self.actionExit.triggered.connect(QtWidgets.qApp.quit)

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

    def _fcn_menu_disp_crossec(self):
        """Display/hide the Cross-sections."""
        viz = self.menuDispCrossec.isChecked()
        # Split view :
        self._fcn_crossec_split()
        # Set cross-sections visible/hide :
        self.volume.visible_cs = viz
        self.grpSec.setChecked(viz)
        # Disable split view if not visible :
        if not viz:
            self._objsPage.setCurrentIndex(0)
            self.view.canvas.show(True)
        # Check (min, max) of slider :
        self._fcn_crossec_sl_limits()

    def _fcn_menu_disp_vol(self):
        """Display/hide the volume."""
        viz = self.menuDispVol.isChecked()
        # Set volume visible/hide :
        self.volume.visible_vol = viz
        self.grpVol.setChecked(viz)

    def _fcn_menu_disp_sources(self):
        """Display/hide sources."""
        viz = self.menuDispSources.isChecked()
        self.sources.visible_obj = viz
        self._s_grp.setChecked(viz)

    def _fcn_menu_disp_connect(self):
        """Display/hide connectivity."""
        viz = self.menuDispConnect.isChecked()
        self.connect.visible_obj = viz
        self._c_grp.setChecked(viz)

    def _fcn_menu_disp_roi(self):
        """Display/hide ROI."""
        try:
            self.volume.mesh.visible = self.menuDispROI.isChecked()
        except:
            pass

    def _fcn_menu_disp_cbar(self):
        """Display/hide the colorbar."""
        viz = self.menuDispCbar.isChecked()
        toggle_enable_tab(self.QuickSettings, 'Cbar', viz)
        self.cbpanelW.setVisible(viz)

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
        if self.volume.name_roi == 'ROI':
            self.volume.mesh.set_camera(camera)
        self.view.wc.update()
        if camera.name == 'turntable':
            self.atlas.rotate(fixed='axial_0')

    ###########################################################################
    #                           PROJECTIONS
    ###########################################################################
    def _fcn_menu_projection(self):
        """Run the cortical projection."""
        self._tprojectas = 'activity'
        self._fcn_source_proj()

    def _fcn_menu_repartition(self):
        """Run the cortical projection."""
        self._tprojectas = 'repartition'
        self._fcn_source_proj()
