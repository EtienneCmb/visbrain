import numpy as np

import vispy.scene.cameras as viscam

from ...utils import slider2opacity

__all__ = ['uiAtlas']

class uiAtlas(object):

    """ui for atlas
    """
    
    def __init__(self,):
        # --------------- MNI ---------------
        # Show/hide :
        self.show_MNI.clicked.connect(self.display_MNI)
        self.Lhemi_only.clicked.connect(self.display_MNI)
        self.Rhemi_only.clicked.connect(self.display_MNI)
        # Projection :
        if self.atlas.projection is 'internal':self.q_internal.setChecked(True)
        elif self.atlas.projection is 'external':self.q_external.setChecked(True)
        self.q_internal.clicked.connect(self.fcn_internal_external)
        self.q_external.clicked.connect(self.fcn_internal_external)


    def display_MNI(self):
        """Display/hide MNI
        """
        # Show/hide MNI :
        self.atlas.mesh.visible = self.show_MNI.isChecked()
        # Hemisphere Left/Right :
        if self.Lhemi_only.isChecked():
            self.xInvert.setChecked(False)
            self.xSlices.setValue(0)
        elif self.Rhemi_only.isChecked():
            self.xInvert.setChecked(True)
            self.xSlices.setValue(0)
        self.fcn_xyzSlice()


    def fcn_internal_external(self):
        """Internal projection
        """
        if self.q_internal.isChecked():
            self.atlas.mesh.projection('internal')
        elif self.q_external.isChecked():
            self.atlas.mesh.projection('external')
        self.atlas.mesh.update()
