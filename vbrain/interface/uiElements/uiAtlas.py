import numpy as np

import vispy.scene.cameras as viscam

from ...utils import slider2opacity, uiSpinValue

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

        # --------------- LIGHT ---------------
        # Position :
        self.uil_posX.valueChanged.connect(self.uiSet_light)
        self.uil_posY.valueChanged.connect(self.uiSet_light)
        self.uil_posZ.valueChanged.connect(self.uiSet_light)
        # Intensity :
        self.uil_intX.valueChanged.connect(self.uiSet_light)
        self.uil_intY.valueChanged.connect(self.uiSet_light)
        self.uil_intZ.valueChanged.connect(self.uiSet_light)
        # Color :
        self.uil_colR.valueChanged.connect(self.uiSet_light)
        self.uil_colG.valueChanged.connect(self.uiSet_light)
        self.uil_colB.valueChanged.connect(self.uiSet_light)
        self.uil_colA.valueChanged.connect(self.uiSet_light)
        # Coeffient :
        self.uil_AmbCoef.valueChanged.connect(self.uiSet_light)
        self.uil_SpecCoef.valueChanged.connect(self.uiSet_light)

        self.uiUpdate_light()


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


    def rotate_fixed(self, vtype='axial'):
        """
        """
        # Coronal (front, back)
        if vtype is 'sagittal':
            if self.atlas.coronal == 0: # Top
                azimuth, elevation = 180, 0
                self.atlas.coronal = 1
            elif self.atlas.coronal == 1: # Bottom
                azimuth, elevation = 0, 0
                self.atlas.coronal = 0
            self.atlas.sagittal, self.atlas.axial = 0, 0
        # Sagittal (left, right)
        elif vtype is 'coronal':
            if self.atlas.sagittal == 0: # Top
                azimuth, elevation = -90, 0
                self.atlas.sagittal = 1
            elif self.atlas.sagittal == 1: # Bottom
                azimuth, elevation = 90, 0
                self.atlas.sagittal = 0
            self.atlas.coronal, self.atlas.axial = 0, 0
        # Axial (top, bottom)
        elif vtype is 'axial':
            if self.atlas.axial == 0: # Top
                azimuth, elevation = 0, 90
                self.atlas.axial = 1
            elif self.atlas.axial == 1: # Bottom
                azimuth, elevation = 0, -90
                self.atlas.axial = 0
            self.atlas.sagittal, self.atlas.coronal = 0, 0

        # Set camera and range :
        self.view.wc.camera.azimuth = azimuth
        self.view.wc.camera.elevation = elevation
        self.view.wc.camera.set_range(x=(-50,50), y=(-50,50), z=(-85,85))

    def uiSet_light(self):
        """
        """
        # Position :
        l_pos = (self.uil_posX.value(), self.uil_posY.value(), self.uil_posZ.value())
        # Intensity :
        l_int = (self.uil_intX.value(), self.uil_intY.value(), self.uil_intZ.value())
        # Color :
        l_col = (self.uil_colR.value(), self.uil_colG.value(), self.uil_colB.value(), self.uil_colA.value())
        # Coef :
        l_amb, l_spec = self.uil_AmbCoef.value(), self.uil_SpecCoef.value()

        self.atlas.mesh.set_light(l_position=l_pos, l_color=l_col, l_intensity=l_int,
                                  l_coefAmbient=l_amb, l_coefSpecular=l_spec)

    def uiUpdate_light(self):
        """
        """
        uiSpinValue([self.uil_posX, self.uil_posY, self.uil_posZ,
                     self.uil_intX, self.uil_intY, self.uil_intZ,
                     self.uil_colR, self.uil_colG, self.uil_colB, self.uil_colA,
                     self.uil_AmbCoef, self.uil_SpecCoef], self.atlas.mesh.get_light)