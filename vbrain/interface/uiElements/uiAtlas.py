import numpy as np

import vispy.scene.cameras as viscam

from ...utils import slider2opacity, uiSpinValue

__all__ = ['uiAtlas']

class uiAtlas(object):

    """ui for atlas
    """
    
    def __init__(self,):

        # Update opacity slider :
        self.OpacitySlider.setValue(self.atlas.opacity*100)

        # ***********************************************************
        # MNI
        # **********************************************************
        # Show/hide :
        self.show_MNI.clicked.connect(self.display_MNI)
        self.Both_only.clicked.connect(self.display_MNI)
        self.Lhemi_only.clicked.connect(self.display_MNI)
        self.Rhemi_only.clicked.connect(self.display_MNI)

        self.uiSwitchTemplate.currentIndexChanged.connect(self.display_MNI)
        self.uiSwitchTemplate.setCurrentIndex(int(self.atlas.template[-1])-1)

        # Projection :
        if self.atlas.projection is 'internal':self.q_internal.setChecked(True)
        elif self.atlas.projection is 'external':self.q_external.setChecked(True)
        self.q_internal.clicked.connect(self.fcn_internal_external)
        self.q_external.clicked.connect(self.fcn_internal_external)


        self.struct_color_edit.setPlaceholderText("Ex: 'red', #ab4642, (1,0,0...)")


    def display_MNI(self):
        """Display/hide MNI
        """
        # Get template :
        self.atlas.template = self.uiSwitchTemplate.currentText()
        # Show/hide MNI :
        self.atlas.mesh.visible = self.show_MNI.isChecked()

        # Hemisphere Both/Left/Right :
        if self.Both_only.isChecked():
            self.atlas.reload(hemisphere='both')
        elif self.Lhemi_only.isChecked():
            self.atlas.reload(hemisphere='left')
        elif self.Rhemi_only.isChecked():
            self.atlas.reload(hemisphere='right')


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
