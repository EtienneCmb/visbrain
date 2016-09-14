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
        self.vert, faces = self.load(self.template, self.user_vert, self.user_faces, self.opacity, self.color,
                                     self.transform, self.user_transform)
        self.plot(self.vert, faces, self.shading, self.projection)


    def __len__(self):
        return len(self.vert)


    def __iter__(self):
        for k in range(len(self)):
            yield self.vert[k, :]


    def _load_surf_template(self, path, template):
        """Load a template atlas
        """
        atlas = np.load(path+'atlas_{template}.npz'.format(template=template))
        return atlas['coord'], atlas['tri']


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
                vertices, faces = self._load_surf_template(self.atlaspath, template)
            else:
                raise ValueError("a_template should be 'B1', 'B2' or 'B3.'")
        # Load a user template
        else:
            vertices, face = self._load_surf_custom(vertices, faces)

        # Preprocessed vertices/faces :
        vertices, faces = self._preprocessing(vertices, faces, color, opacity, transform, user_transform)

        return vertices, faces

    def _preprocessing(self, vertices, faces, color, opacity, transform, user_transform):
        """
        """
        # Get some usefull variables :
        self._nv = vertices.size//3

        # Default vcolor :
        self.d_vcolor = color2vb(color=color, default=self._defcolor, length=self._nv, alpha=opacity)

        # Inspect minimum and maximum :
        vm, vM = np.abs(vertices).min(), np.abs(vertices).max()
        self._factor = self._scaleMax/vM

        # User transformation :
        if self.user_transform is not None:
            vertices = self.user_transform.map(vertices)[:, 0:-1]

        # Rescale coordinates :
        if transform is not None:
            # Set everything around zero :
            transform.prepend(vist.STTransform(translate=list(-vertices.mean(0))))
            # Rescale vertices coordinates :
            transform.prepend(vist.STTransform(scale=[self._factor]*3))
            # Apply transformation :
            vertices = transform.map(vertices)[:, 0:-1]

        # Keep maximum/minimum pear coordinates :
        self._vertsize = [(vertices[:, 0].min(), vertices[:, 0].max()),
                          (vertices[:, 1].min(), vertices[:, 1].max()),
                          (vertices[:, 2].min(), vertices[:, 2].max())]

        return vertices, faces
        

    def plot(self, vertices, faces, shading='smooth', projection='internal'):
        """Mesh the brain
        """
        # Get data and mesh :
        meshdata = visg.MeshData(vertices=vertices, faces=faces, vertex_colors=self.d_vcolor)
        self.mesh = visu.Mesh(meshdata=meshdata, shading=shading, name='Brain')
        self.mask = np.zeros((len(self),), dtype=bool)

        # Internal/external projection :
        if projection is 'internal':
            self.mesh.set_gl_state('translucent', depth_test=False, cull_face=True)
        elif projection is 'external':
            self.mesh.set_gl_state('translucent', depth_test=True, cull_face=False, polygon_offset_fill=True)

    def reload(self):
        """
        """
        vbAtlas.__init__(self)