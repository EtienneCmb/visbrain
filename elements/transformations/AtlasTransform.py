import numpy as np

class AtlasTransform(object):

    """docstring for AtlasTransform
    """

    def __init__(self, **kwargs):
        pass

    def set_alpha(self, alpha):
        """
        """
        # Get vertices and color :
        vcolor = self.atlas.mesh.mesh_data.get_vertex_colors()
        vcolor[:, 3] = alpha

        # Update vertex colors :
        self.atlas.mesh.mesh_data.set_vertex_colors(vcolor)
        self.atlas.mesh.mesh_data_changed()


    def switch_internal_external(self, projection):
        """
        """
        if projection == 'internal':
            self.atlas.mesh.set_gl_state('translucent', depth_test=False, cull_face=True, blend=True, blend_func=('src_alpha', 'one_minus_src_alpha'))
        else:
            self.atlas.mesh.set_gl_state('translucent', depth_test=True, cull_face=False, blend=True, blend_func=('src_alpha', 'one_minus_src_alpha'))
        self.atlas.mesh.update_gl_state()

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
        self.view.wc.camera.set_range(x=self.atlas._vertsize[0], y=self.atlas._vertsize[1],
                                      z=self.atlas._vertsize[2], margin=0.05)