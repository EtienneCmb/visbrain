import os
import numpy as np

import vispy.scene.visuals as visu
import vispy.geometry as visg
import vispy.visuals.transforms as vist 

from ..utils import color2vb

import visbrain


class AtlasBase(object):

    """
    """

    def __init__(self, canvas, **kwargs):
        # Get inputs :
        self.canvas = canvas
        self.opacity = kwargs['a_opacity']
        self.color = kwargs['a_color']
        self.template = kwargs['a_template']
        self.projection = kwargs['a_projection']
        self.transform = kwargs['a_transform']
        self.shading = kwargs['a_shading']
        self.user_vert = kwargs['a_vertices']
        self.user_faces = kwargs['a_faces']

        # Needed variables :
        self.atlaspath = os.path.dirname(visbrain.__file__)+'/elements/templates/'
        self._defcolor = (1,1,1)
        self._scaleMax = 100

        # Initialize visualization :
        self.vert, faces = self.load(self.template, self.user_vert, self.user_faces, self.opacity, self.color, self.transform)
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


    def load(self, template='B1', vertices=None, faces=None, opacity=0.1, color=(1,1,1), transform=None):
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

        # Get some usefull variables :
        self._nv = vertices.size//3

        # Default vcolor :
        self.d_vcolor = color2vb(color=color, default=self._defcolor, length=self._nv, alpha=opacity)

        # Inspect minimum and maximum :
        vm, vM = np.abs(vertices).min(), np.abs(vertices).max()
        self._factor = self._scaleMax/vM

        # Rescale coordinates :
        if transform is not None:
            transform.append(vist.STTransform(scale=[self._factor]*3))
            vertices = transform.map(vertices)[:, 0:-1]

        return vertices, faces


    def plot(self, vertices, faces, shading='smooth', projection='internal'):
        """Mesh the brain
        """
        # Get data and mesh :
        meshdata = visg.MeshData(vertices=vertices, faces=faces, vertex_colors=self.d_vcolor)
        self.mesh = visu.Mesh(meshdata=meshdata, shading=shading, name='BrainMNI')
        
        # Internal/external projection :
        if projection is 'internal':
            self.mesh.set_gl_state('translucent', depth_test=False, cull_face=True)
        elif projection is 'external':
            self.mesh.set_gl_state('translucent', depth_test=True, cull_face=False)
        self.mesh.update()

        # Add to the canvas :
        self.canvas.add(self.mesh)


    def reload(self):
        """
        """
        vbAtlas.__init__(self)