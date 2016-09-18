import os
import numpy as np

import vispy.scene.visuals as visu
import vispy.geometry as visg
import vispy.visuals.transforms as vist

from ..utils import color2vb
from ..visuals import BrainMesh

import visbrain


class AtlasBase(object):

    """
    """

    def __init__(self, a_color=(1.0,1.0,1.0), a_opacity=0.1, a_projection='internal', a_template='B1',
                 a_vertices=None, a_faces=None, a_shading='smooth', a_transform=[], l_position=(100., 100., 100.),
                 l_intensity=(1., 1., 1.), l_color=(1., 1., 1., 1.), l_coefAmbient=0.05, l_coefSpecular=0.5, **kwargs):
        # Get inputs :
        self.color = a_color
        self.opacity = a_opacity
        self.template = a_template
        self.projection = a_projection
        self.transform = a_transform
        self.shading = a_shading
        self.user_vert = a_vertices
        self.user_faces = a_faces
        self.sagittal, self.coronal, self.axial = (0, 0, 0)
        self.l_pos, self.l_int, self.l_col = l_position, l_intensity, l_color
        self.l_amb, self.l_spec = l_coefAmbient, l_coefSpecular

        # Needed variables :
        self.atlaspath = os.path.dirname(visbrain.__file__)+'/vbrain/elements/templates/'
        self._defcolor = (1,1,1)
        self._scaleMax = 100

        # Initialize visualization :
        vertices, normals, color, faces = self.load(self.template, self.user_vert, self.user_faces)
        self.plot(vertices, normals, color, faces, a_projection)


    def __len__(self):
        return len(self.vert)


    def __iter__(self):
        for k in range(len(self)):
            yield self.vert[k, ...]


    def load(self, template='B1', vertices=None, faces=None):
        """Load the atlas to use for the interface.
        """
        # Load a default template :
        if (vertices is None) and (faces is None):
            if (template in ['B1', 'B2', 'B3']):
                atlas = np.load(self.atlaspath+'atlasGL_{template}.npz'.format(template=template))
                faces, normals = atlas['faces'], atlas['a_normal']
                vertices, color = atlas['a_position'], atlas['a_color']
            else:
                raise ValueError("a_template should be 'B1', 'B2' or 'B3.'")
        # Load a user template
        else:
            vertices, faces, normals, color = vertices, faces, None, None

        return vertices, normals, color, faces


    def plot(self, vertices, normals, color, faces, projection):
        """Mesh the brain
        """
        # Initialize mesh object : :
        self.mesh = BrainMesh(vertices=vertices, faces=faces, normals=normals, name='Brain',
                              l_position=self.l_pos, l_intensity=self.l_int, l_color=self.l_col,
                              l_coefAmbient=self.l_amb,  l_coefSpecular=self.l_spec,
                              scale_factor=self._scaleMax)
        self.vert = self.mesh.get_vertices
        self.transform = self.mesh._btransform
        self.mask = np.zeros((len(self.mesh), 3), dtype=bool)
        self._nv = len(self.mesh)

        self.mesh.set_alpha(self.opacity)
        # Internal/external projection :
        self.mesh.projection(projection)
