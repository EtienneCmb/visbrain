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
                 a_vertices=None, a_faces=None, a_shading='smooth', a_transform=[], t_transform=None, **kwargs):
        # Get inputs :
        self.color = a_color
        self.opacity = a_opacity
        self.template = a_template
        self.projection = a_projection
        self.user_transform = t_transform # user transformation
        self.transform = a_transform      # software transformations
        self.shading = a_shading
        self.user_vert = a_vertices
        self.user_faces = a_faces
        self.sagittal = 0
        self.coronal = 0
        self.axial = 0

        # Needed variables :
        self.atlaspath = os.path.dirname(visbrain.__file__)+'/vbrain/elements/templates/'
        self._defcolor = (1,1,1)
        self._scaleMax = 100

        # Initialize visualization :
        self.vert, normals, color, faces = self.load(self.template, self.user_vert, self.user_faces, self.opacity,
                                                    self.color, self.transform, self.user_transform)
        self.plot(self.vert, normals, color, faces, a_projection)


    def __len__(self):
        return len(self.vert)


    def __iter__(self):
        for k in range(len(self)):
            yield self.vert[k, :]


    def _load_surf_template(self, path, template):
        """Load a template atlas
        """
        atlas = np.load(path+'atlasGL_{template}.npz'.format(template=template))
        faces = atlas['faces']
        normals = atlas['a_normal']
        vertices = atlas['a_position']
        color = atlas['a_color']
        return vertices, normals, color, faces


    def _load_surf_custom(self, vertices, faces):
        """Load a custom atlas
        """
        # Check shapes :
        if 3 not in vertices.shape:
            raise ValueError("Vertices must be (N, 3) array.")
        if vertices.shape[1] != 3:
            vertices = vertices.T
        if 3 not in faces.shape:
            raise ValueError("Faces must be (N, 3) array.")
        if faces.shape[1] != 3:
            faces = faces.T
        if faces.min() != 0: # Matlab users
            faces -= faces.min()
        return vertices, faces


    def load(self, template='B1', vertices=None, faces=None, opacity=0.1, color=(1,1,1), transform=None,
             user_transform=None):
        """Load the atlas to use for the interface.
        """
        # Load a default template :
        if (vertices is None) and (faces is None):
            if (template in ['B1', 'B2', 'B3']):
                vertices, normals, color, faces = self._load_surf_template(self.atlaspath, template)
            else:
                raise ValueError("a_template should be 'B1', 'B2' or 'B3.'")
        # Load a user template
        else:
            vertices, face = self._load_surf_custom(vertices, faces)

        return vertices, normals, color, faces


    def plot(self, vertices, normals, color, faces, projection):
        """Mesh the brain
        """
        # Get data and mesh :
        self.mesh = BrainMesh(vertices=vertices, faces=faces, normals=normals, name='Brain',
                              l_position=(10., 10., 10.), scale_factor=self._scaleMax)
        self.transform = self.mesh._btransform
        self.mask = np.zeros((len(self.mesh),), dtype=bool)
        self._nv = len(self.mesh)

        self.mesh.set_alpha(self.opacity)
        # Internal/external projection :
        self.mesh.projection(projection)
