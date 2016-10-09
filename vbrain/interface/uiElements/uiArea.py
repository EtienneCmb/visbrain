import numpy as np
from ...utils import textline2color


__all__ = ['uiArea']


class uiArea(object):

    """ui for atlas
    """
    
    def __init__(self,):
        # By default, hide panels :
        self.structPanel.hide()
        self.struct_rmvLst.hide()
        self.area.color = 'lightgray'

        # Get plot properties :
        self.structEnable.clicked.connect(self.fcn_show_hide_struct_panel)
        self.Sub_brod.clicked.connect(self.fcn_buildStruct)
        self.Sub_aal.clicked.connect(self.fcn_buildStruct)
        self.struct_color_edit.editingFinished.connect(self.fcn_colorStruct)

        # List management :
        self.struct2select.itemClicked.connect(self.fcn_lst_add)
        self.struct2add.itemClicked.connect(self.fcn_lst_rmv)
        self.struct_addLst.clicked.connect(self.fcn_add_struct)
        self.struct_rmvLst.clicked.connect(self.fcn_rmv_struct)
        self.struct_rstLst.clicked.connect(self.fcn_rst_struct)
        self._struct2add = []

        # Internal/external projection :
        self.struct_External.clicked.connect(self.fcn_InternalExternal)
        self.struct_Internal.clicked.connect(self.fcn_InternalExternal)

        # System :
        self.strcutShow.clicked.connect(self.fcn_visible_area)
        self.struct_apply.clicked.connect(self.fcn_applyStruct)

        self.fcn_buildStruct()



    #########################################################################
    # MANAGE LIST
    #########################################################################
    # List click (show/hide buttons) :
    def fcn_lst_add(self):
        """
        """
        # Manage buttons :
        self.struct_rmvLst.hide()
        self.struct_addLst.show()


    def fcn_lst_rmv(self):
        """
        """
        # Manage buttons :
        self.struct_addLst.hide()
        self.struct_rmvLst.show()


    # Add/remove elements to the list :
    def fcn_add_struct(self):
        """
        """
        currentItem = [k.text() for k in self.struct2select.selectedItems()]
        for k in currentItem:
            if k not in self._struct2add:
                self._struct2add.append(k)
            self.fcn_update_list()


    def fcn_rmv_struct(self):
        """
        """
        currentItem = self.struct2add.currentItem().text()
        self._struct2add.pop(self._struct2add.index(currentItem));
        self.fcn_update_list()


    def fcn_update_list(self):
        """
        """
        # Update list :
        self.struct2add.clear()
        self._struct2add.sort()
        self.struct2add.addItems(self._struct2add)


    def fcn_rst_struct(self):
        """
        """
        self.struct2add.clear()
        self._struct2add = []


    #########################################################################
    # AREA PROCESS
    #########################################################################
    def fcn_buildStruct(self):
        """
        """
        # Get current structure :
        if self.Sub_brod.isChecked():
            self.area.structure = 'brod'
        elif self.Sub_aal.isChecked():
            self.area.structure = 'aal'

        # Update list of structures :
        self.struct2select.clear()
        self.struct2select.addItems(self.area._label)
        self.fcn_rst_struct()
            
        # Reconstruct structure list :
        self.area._preprocess()

    def fcn_applyStruct(self):
        """
        """
        struct2add = [int(k.split(':')[0]) for k in self._struct2add]
        struct2add.sort()
        self.area.select = struct2add
        self.area._get_vertices()
        self.area._plot()
        self.area.mesh.parent = self._vbNode
        self.area.set_camera(self.view.wc.camera)


    def fcn_InternalExternal(self):
        """
        """
        if self.struct_Internal.isChecked():
            self.area.mesh.projection('internal')
        elif self.struct_External.isChecked():
            self.area.mesh.projection('external')


    def fcn_colorStruct(self):
        """
        """
        self.area.color = tuple(textline2color(self.struct_color_edit.text())[1][0])
        try:
            self.area.set_color(self.area.color)
        except:
            pass

    #########################################################################
    # PANEL AND VISIBILITY
    #########################################################################
    def fcn_show_hide_struct_panel(self):
        """
        """
        self.structPanel.setVisible(self.structEnable.isChecked())


    def fcn_visible_area(self):
        """
        """
        self.area.mesh.visible = self.strcutShow.isChecked()




