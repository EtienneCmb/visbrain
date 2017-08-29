"""GUI interactions with the contextual menu."""
from PyQt5 import QtWidgets
import vispy.scene.cameras as viscam

from ....utils import toggle_enable_tab, HelpMenu

__all__ = ('uiMenu')


class uiMenu(HelpMenu):
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
        self.menuDispQuickSettings.triggered.connect(self._fcn_menuDispSet)
        # Brain :
        self.menuDispBrain.triggered.connect(self._fcn_menuBrain)
        # Cross-sections :
        self.menuDispCrossec.triggered.connect(self._fcn_menuCrossec)
        # Volume :
        self.menuDispVol.triggered.connect(self._fcn_menuVol)
        # Sources :
        self.menuDispSources.triggered.connect(self._fcn_menuSources)
        # Connectivity :
        self.menuDispConnect.triggered.connect(self._fcn_menuConnect)
        # ROI :
        self.menuDispROI.triggered.connect(self._fcn_menuROI)
        # Colorbar :
        self.menuDispCbar.triggered.connect(self._fcn_menuCbar)

        # =============================================================
        # ROTATION
        # =============================================================
        self.menuRotTop.triggered.connect(self._fcn_rotateTop)
        self.menuRotBottom.triggered.connect(self._fcn_rotateBottom)
        self.menuRotLeft.triggered.connect(self._fcn_rotateLeft)
        self.menuRotRight.triggered.connect(self._fcn_rotateRight)
        self.menuRotFront.triggered.connect(self._fcn_rotateFront)
        self.menuRotBack.triggered.connect(self._fcn_rotateBack)

        # =============================================================
        # CAMERA
        # =============================================================
        self.menuCamFly.triggered.connect(self._fcn_setCamFly)

        # =============================================================
        # PROJECTIONS
        # =============================================================
        self.menuCortProj.triggered.connect(self._fcn_menuProjection)
        self.menuCortRep.triggered.connect(self._fcn_menuRepartition)

    def _fcn_show_screenshot(self):
        """Display the screenshot GUI."""
        self.show_gui_screenshot()

    ###########################################################################
    #                                DISPLAY
    ###########################################################################
    def _fcn_menuDispSet(self):
        """Toggle method for display / hide the settings panel."""
        viz = self.menuDispQuickSettings.isChecked()
        self.q_widget.setVisible(viz)

    def _fcn_menuBrain(self):
        """Display/hide the main Brain."""
        viz = self.menuDispBrain.isChecked()
        self.atlas.mesh.visible = viz
        self.o_Brain.setEnabled(viz)
        self.o_Brain.setChecked(viz)

    def _fcn_menuCrossec(self):
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

    def _fcn_menuVol(self):
        """Display/hide the volume."""
        viz = self.menuDispVol.isChecked()
        # Set volume visible/hide :
        self.volume.visible_vol = viz
        self.grpVol.setChecked(viz)

    def _fcn_menuSources(self):
        """Display/hide sources."""
        inn = self.sources.mesh.name != 'NoneSources'
        viz = self.menuDispSources.isChecked() and inn
        self.sources.mesh.visible = viz
        self.sources.stextmesh.visible = viz
        self.grpText.setChecked(viz)
        self.toolBox.setEnabled(viz)
        self.toolBox.setEnabled(viz)
        self.groupBox_6.setEnabled(viz)
        self.o_Sources.setEnabled(viz)
        self.o_Sources.setChecked(viz)
        self.o_Text.setEnabled(viz)
        self.o_Text.setChecked(viz)

    def _fcn_menuConnect(self):
        """Display/hide connectivity."""
        inn = self.connect.mesh.name != 'NoneConnect'
        viz = self.menuDispConnect.isChecked() and inn
        self.connect.mesh.visible = viz
        self.toolBox_5.setEnabled(viz)
        self.toolBox_6.setEnabled(viz)
        self.o_Connect.setEnabled(viz)
        self.o_Connect.setChecked(viz)

    def _fcn_menuROI(self):
        """Display/hide ROI."""
        try:
            self.volume.mesh.visible = self.menuDispROI.isChecked()
        except:
            pass

    def _fcn_menuCbar(self):
        """Display/hide the colorbar."""
        viz = self.menuDispCbar.isChecked()
        toggle_enable_tab(self.QuickSettings, 'Cbar', viz)
        self.cbpanelW.setVisible(viz)
        # Get enabled objects :
        cbox = self.cbqt.cbui.object
        objs = [cbox.model().item(k).isEnabled() for k in range(cbox.count())]
        if sum(objs) == 1:
            # Select the name of the enabled object :
            self.cbqt.select(cbox.itemText(objs.index(True)))

    ###########################################################################
    #                                ROTATION
    ###########################################################################
    def _fcn_rotateTop(self):
        """Display top scene."""
        self._rotate('axial_0')

    def _fcn_rotateBottom(self):
        """Display bottom scene."""
        self._rotate('axial_1')

    def _fcn_rotateLeft(self):
        """Display left scene."""
        self._rotate('sagittal_0')

    def _fcn_rotateRight(self):
        """Display ritgh scene."""
        self._rotate('sagittal_1')

    def _fcn_rotateFront(self):
        """Display front scene."""
        self._rotate('coronal_0')

    def _fcn_rotateBack(self):
        """Display back scene."""
        self._rotate('coronal_1')

    ###########################################################################
    #                                CAMERA
    ###########################################################################
    def _fcn_setCamFly(self):
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
            self._rotate(fixed='axial_0')

    ###########################################################################
    #                           PROJECTIONS
    ###########################################################################
    def _fcn_menuProjection(self):
        """Run the cortical projection."""
        self._tprojectas = 'activity'
        self._sourcesProjection()

    def _fcn_menuRepartition(self):
        """Run the cortical projection."""
        self._tprojectas = 'repartition'
        self._sourcesProjection()
