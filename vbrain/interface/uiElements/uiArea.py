import numpy as np


__all__ = ['uiArea']


class uiArea(object):

    """ui for atlas
    """
    
    def __init__(self,):
        # By default, hide panels :
        self.structPanel.hide()
        self.structPanelSelect.hide()

        # Get plot properties :
        self.structEnable.clicked.connect(self.fcn_buildStruct)
        self.Sub_brod.clicked.connect(self.fcn_buildStruct)
        self.Sub_aal.clicked.connect(self.fcn_buildStruct)
        self.struct_all.clicked.connect(self.fcn_buildStruct)
        self.struct_specific.clicked.connect(self.fcn_buildStruct)

        # Internal/external projection :
        self.struct_External.clicked.connect(self.fcn_InternalExternal)
        self.struct_Internal.clicked.connect(self.fcn_InternalExternal)

        # System :
        self.strcutShow.clicked.connect(self.fcn_visble_area)
        self.struct_apply.clicked.connect(self.fcn_applyStruct)

    def fcn_buildStruct(self):
        """
        """
        # Get current structure :
        if self.Sub_brod.isChecked():
            self.area.structure = 'brod'
        elif self.Sub_aal.isChecked():
            self.area.structure = 'aal'

        # Get color/colormap properties :
        if self.structUniform.isChecked():
            self.area.color = 'white'
        elif self.struct_specific.isChecked():
            pass
            # self.area.color = self.struct_color_edit.currentText()

        # Update list of structures :
        self.struct_list.clear()
        self.struct_list.addItems(self.area._label)

        # Get selected areas :
        if self.struct_all.isChecked():
            self.area.select = None
        elif struct_specific.isChecked():
            self.area.select = []
        self.area.select = [4, 6, 32, 40]
            
        # Reconstruct brodmann structure :

        self.area._preprocess()

    def fcn_applyStruct(self):
        """
        """
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


    def fcn_visble_area(self):
        """
        """
        self.area.mesh.visible = self.strcutShow.isChecked()




