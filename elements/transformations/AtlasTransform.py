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