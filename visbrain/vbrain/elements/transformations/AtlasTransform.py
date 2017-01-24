import numpy as np

class AtlasTransform(object):

    """docstring for AtlasTransform
    """

    def __init__(self, **kwargs):
        pass


    # def rotate_fixed(self, vtype='axial'):
    #     """
    #     """
    #     # Coronal (front, back)
    #     if vtype is 'sagittal':
    #         if self.atlas.coronal == 0: # Top
    #             azimuth, elevation = 180, 0
    #             self.atlas.coronal = 1
    #         elif self.atlas.coronal == 1: # Bottom
    #             azimuth, elevation = 0, 0
    #             self.atlas.coronal = 0
    #         self.atlas.sagittal, self.atlas.axial = 0, 0
    #     # Sagittal (left, right)
    #     elif vtype is 'coronal':
    #         if self.atlas.sagittal == 0: # Top
    #             azimuth, elevation = -90, 0
    #             self.atlas.sagittal = 1
    #         elif self.atlas.sagittal == 1: # Bottom
    #             azimuth, elevation = 90, 0
    #             self.atlas.sagittal = 0
    #         self.atlas.coronal, self.atlas.axial = 0, 0
    #     # Axial (top, bottom)
    #     elif vtype is 'axial':
    #         if self.atlas.axial == 0: # Top
    #             azimuth, elevation = 0, 90
    #             self.atlas.axial = 1
    #         elif self.atlas.axial == 1: # Bottom
    #             azimuth, elevation = 0, -90
    #             self.atlas.axial = 0
    #         self.atlas.sagittal, self.atlas.coronal = 0, 0

    #     # Set camera and range :
    #     self.view.wc.camera.azimuth = azimuth
    #     self.view.wc.camera.elevation = elevation
    #     # self.view.wc.camera.set_range(x=self.atlas._vertsize[0], y=self.atlas._vertsize[1],
    #     #                               z=self.atlas._vertsize[2], margin=0.05)