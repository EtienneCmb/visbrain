"""Base class for the MNI brain:
- load the template (default or a custom one)
- create the MNI (BrainMesh)
- reload function to change template
"""

import os
import numpy as np

import vispy.scene.visuals as visu
import vispy.geometry as visg
import vispy.visuals.transforms as vist

from ..utils import color2vb
from ..visuals import BrainMesh

import visbrain


class AtlasBase(object):

    """Base class for atlas managment. From all inputs arguments, this class
    use only those containing 'a_' (atlas) and 'l_' (light). 
    """

    def __init__(self, a_color=(1.0,1.0,1.0), a_opacity=1., a_projection='internal',
                 a_template='B1', a_hemisphere='both', a_vertices=None, a_faces=None,
                 a_shading='smooth', a_transform=[], l_position=(100., 100., 100.),
                 l_intensity=(1., 1., 1.), l_color=(1., 1., 1., 1.), l_coefAmbient=0.05,
                 l_coefSpecular=0.5, **kwargs):
        # Get inputs :
        self.color = a_color
        self.opacity = a_opacity
        self.template = a_template
        self.projection = a_projection
        self.transform = a_transform
        self.shading = a_shading
        self.user_vert = a_vertices
        self.user_faces = a_faces
        self.hemisphere = a_hemisphere
        self.sagittal, self.coronal, self.axial = (0, 0, 0)
        self.l_pos, self.l_int, self.l_col = l_position, l_intensity, l_color
        self.l_amb, self.l_spec = l_coefAmbient, l_coefSpecular

        # Needed variables :
        self.atlaspath = os.path.dirname(visbrain.__file__)+'/vbrain/vbobj/templates/'
        self._defcolor = (1,1,1)
        self._scaleMax = 100

        # Initialize visualization :
        vertices, faces, normals, color = self.load(self.template, self.user_vert,
                                                    self.user_faces)
        self.plot(vertices, faces, normals, color, a_projection, a_hemisphere)


    def __len__(self):
        return len(self.vert)


    def __iter__(self):
        for k in range(len(self)):
            yield self.vert[k, ...]


    def load(self, template='B1', vertices=None, faces=None):
        """Load the atlas to use for the interface. Use either a default
        or a custom template using the vertices and faces inputs.

        Kargs:
            template: string, optional, (def: 'B1')
                The template to import. Use either 'B1', 'B2' or
                'B3'.

            vertices: ndarray, optional, (def: None)
                Vertices to set of shape (N, 3) or (M, 3)

            faces: ndarray, optional, (def: None)
                Faces to set of shape (M, 3)

        Returns:
            vertices: ndarray
                Vertices to set of shape (M, 3, 3)

            faces: ndarray
                Faces to set of shape (M, 3)

            normals: ndarray
                Normals per faces (needed for light) of shape (M, 3, 3)

            color: ndarray
                Brain color per faces of shape (M, 3, 4) for RGBA color
        """
        # Load a default template :
        if (vertices is None) and (faces is None):
            if (template in ['B1', 'B2', 'B3']):
                atlas = np.load(self.atlaspath+'{template}.npz'.format(template=template))
                faces, normals = atlas['faces'], atlas['a_normal']
                vertices, color = atlas['a_position'], atlas['a_color']
            else:
                raise ValueError("a_template should be 'B1', 'B2' or 'B3.'")
        # Load a user template
        else:
            vertices, faces, normals, color = vertices, faces, None, None

        return vertices, faces, normals, color


    def plot(self, vertices=None, faces=None, normals=None, color=None,
             projection='internal', hemisphere='both'):
        """Create the standard MNI brain

        Kargs:
            vertices: ndarray, optional, (def: None)
                Vertices to set of shape (M, 3, 3)

            faces: ndarray, optional, (def: None)
                Faces to set of shape (M, 3)

            normals: ndarray, optional, (def: None)
                The normals to set (same shape as vertices)

            color: ndarray, optional, (def: None)
                Brain color array of shape (M, 3, 4) for RGBA color

            projection: string, optional, (def: 'internal')
                Project light either inside ('internal') or outside
                ('external') of the brain.

            hemisphere: string, optional, (def: 'color')
                Which hemisphere to plot. Use either 'both', 'left' or
                'right'
        """
        # Initialize mesh object :
        self.mesh = BrainMesh(vertices=vertices, faces=faces, normals=normals, name='Brain',
                              l_position=self.l_pos, l_intensity=self.l_int, l_color=self.l_col,
                              l_coefAmbient=self.l_amb,  l_coefSpecular=self.l_spec,
                              scale_factor=self._scaleMax, hemisphere=hemisphere)
        self.vert = self.mesh.get_vertices
        self.transform = self.mesh._btransform
        self.mask = np.zeros((len(self.mesh), 3), dtype=bool)
        self._nv = len(self.mesh)

        self.mesh.set_alpha(self.opacity)
        # Internal/external projection :
        self.mesh.projection(projection)


    def reload(self, template=None, hemisphere=None, projection=None, vertices=None,
               faces=None):
        """Reload an existing MNI brain

        Karg:
            template: string, optional, (def: 'B1')
                The template to import. Use either 'B1', 'B2' or
                'B3'.

            hemisphere: string, optional, (def: 'color')
                Which hemisphere to plot. Use either 'both', 'left' or
                'right'.

            projection: string, optional, (def: 'internal')
                Project light either inside ('internal') or outside
                ('external') of the brain.

            vertices: ndarray, optional, (def: None)
                Vertices to set of shape (N, 3) or (M, 3)

            faces: ndarray, optional, (def: None)
                Faces to set of shape (M, 3)
        """
        if template is not None:
            self.template = template
        if hemisphere is not None:
            self.hemisphere = hemisphere
        if projection is not None:
            self.projection = projection

        # Initialize visualization :
        vertices, faces, normals, color = self.load(self.template, vertices, faces)
        self.mesh.set_data(vertices=vertices, faces=faces, normals=normals,
                           hemisphere=hemisphere)
        self.mesh.set_color(color=self.color)
        self._nv = len(self.mesh)
        self.vert = self.mesh.get_vertices
