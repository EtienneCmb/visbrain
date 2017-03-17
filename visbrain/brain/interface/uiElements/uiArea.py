"""Top level class for linking sub-structures and the GUI.

In visbrain, there's the possibility to add sub-structures (like brodmann,
areas, gyrus...). This script translate graphical buttons into functions. The
structure panel in the GUI is present in the MNI -> Structures tab.
"""

from ....utils import textline2color


__all__ = ['uiArea']


class uiArea(object):
    """Link graphical interface with sub-structures functions."""

    def __init__(self,):
        """Init."""
        # By default, hide panels :
        self.structPanel.hide()
        self.struct_rmvLst.hide()
        self.area.color = 'lightgray'

        # Get plot properties :
        self.structEnable.clicked.connect(self._fcn_show_hide_struct_panel)
        self.Sub_brod.clicked.connect(self._fcn_buildStructLst)
        self.Sub_aal.clicked.connect(self._fcn_buildStructLst)
        self.struct_color_edit.editingFinished.connect(self._fcn_colorStruct)

        # List management :
        self.struct2select.itemClicked.connect(self._fcn_selectStructInLst)
        self.struct2add.itemClicked.connect(self._fcn_selectInAddedStruct)
        self.struct_addLst.clicked.connect(self._fcn_add_struct)
        self.struct_rmvLst.clicked.connect(self._fcn_rmv_struct)
        self.struct_rstLst.clicked.connect(self._fcn_rst_struct)
        self._struct2add = []

        # Internal/external projection :
        self.struct_External.clicked.connect(self._area_light_reflection)
        self.struct_Internal.clicked.connect(self._area_light_reflection)

        # System :
        self.strcutShow.clicked.connect(self._fcn_visible_area)
        self.struct_apply.clicked.connect(self._fcn_applyStruct)
        self.structClear.clicked.connect(self._fcn_roiClear)

        self._fcn_buildStructLst()

    #########################################################################
    # MANAGE LIST OF AREAS
    #########################################################################
    # ---------- List click (show / hide buttons) ----------
    def _fcn_selectStructInLst(self):
        """Trig when a structure is selected in the list.

        When the user select a structure in the whole list, display the 'add'
        button but hide the 'remove' button.
        """
        self.struct_addLst.show()
        self.struct_rmvLst.hide()

    def _fcn_selectInAddedStruct(self):
        """Trig when a structure is selected in the added list.

        When the user select a structure in the list, of selected areas,
        hide the 'add' button but display the 'remove' button.
        """
        self.struct_addLst.hide()
        self.struct_rmvLst.show()

    # ---------- Add / remove / update / reset elements to the list ----------
    def _fcn_add_struct(self):
        """Trig when the user click on the 'add' button.

        This function will add the selected structre but only if it's not
        already present in the list.
        """
        currentItem = [str(k.text())
                       for k in self.struct2select.selectedItems()]
        for k in currentItem:
            if k not in self._struct2add:
                self._struct2add.append(k)
            self._fcn_update_list()

    def _fcn_rmv_struct(self):
        """Trig when the user click on the 'remove' button.

        This function doesn't need any conditional testing because the 'remove'
        button is only showed when a structure is displayed.
        """
        currentItem = str(self.struct2add.currentItem().text())
        self._struct2add.pop(self._struct2add.index(currentItem))
        self._fcn_update_list()

    def _fcn_update_list(self):
        """Update the list of selected areas.

        The list of selected areas has to be updated if the user add / remove
        structures.
        """
        # Update list :
        self.struct2add.clear()
        self._struct2add.sort()
        self.struct2add.addItems(self._struct2add)

    def _fcn_rst_struct(self):
        """Reset to default the list of selected areas.

        Just clean all selected structures.
        """
        self.struct2add.clear()
        self._struct2add = []

    #########################################################################
    # AREA PROCESS
    #########################################################################
    def _fcn_buildStructLst(self):
        """Build the list of avaible structures.

        The list of avaible structures depends on the choice of the atlas
        (Brodmann or AAL). This function update the list of areas depending on
        this choice.
        """
        # Get avaible structures. This is automatically updated because of the
        # use  of @property and setter :
        if self.Sub_brod.isChecked():
            self.area.structure = 'brod'
        elif self.Sub_aal.isChecked():
            self.area.structure = 'aal'
        self.area.update()

        # Update list of structures :
        self.struct2select.clear()
        self.struct2select.addItems(self.area._label)
        self._fcn_rst_struct()

    def _fcn_applyStruct(self):
        """Apply the choice of structures and plot them.

        This function get the list of integers preceding each areas, get the
        vertices and finally plot.
        """
        # Select only the integer preceding the structure :
        struct2add = [int(k.split(':')[0]) for k in self._struct2add]
        struct2add.sort()

        # Add to selected areas and plot :
        self.area.select = struct2add
        self._area_plot()

    def _fcn_roiClear(self):
        """Clear ROI."""
        self.area.mesh.clean()
        self.area.mesh.update()

    def _area_plot(self):
        """Area Sub-plotting function."""
        # Get smoothing :
        self.area.smoothsize = self._roiSmooth.value()
        # Plot areas and set parent :
        self.area.plot()
        self.area.mesh.parent = self._vbNode
        self.area.set_camera(self.view.wc.camera)
        # Enable projection on ROI and related buttons :
        self._uitProjectOn.model().item(1).setEnabled(True)
        self._roiReflect.setEnabled(True)
        self.strcutShow.setEnabled(True)
        self.o_Areas.setEnabled(True)

    def _area_light_reflection(self, *args):
        """Change how light is refleting onto sub-areas.

        This function can be used to see either the surface only (external) or
        deep voxels inside areas (internal).
        """
        if self.struct_Internal.isChecked():
            self.area.mesh.projection('internal')
        elif self.struct_External.isChecked():
            self.area.mesh.projection('external')

    def _fcn_colorStruct(self):
        """Apply colormap to sub-areas."""
        self.area.color = tuple(textline2color(self.struct_color_edit.text(
                                                                ))[1][0])
        try:
            self.area.set_color(self.area.color)
        except:
            pass

    #########################################################################
    # PANEL AND VISIBILITY
    #########################################################################
    def _fcn_show_hide_struct_panel(self):
        """Toggle for display / hide area panel."""
        self.structPanel.setVisible(self.structEnable.isChecked())

    def _fcn_visible_area(self):
        """Set visible area(s) visible or not."""
        self.area.mesh.visible = self.strcutShow.isChecked()
