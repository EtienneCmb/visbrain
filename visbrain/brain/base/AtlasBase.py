"""Base class for the MNI brain.

- load the template (default or a custom one)
- create the MNI (BrainMesh)
- reload function to change template
"""

import os
import sys
import numpy as np
from warnings import warn

from ...visuals import BrainMesh


class AtlasBase(object):
    """Base class for atlas managment.

    From all inputs arguments, this class use only those containing 'a_'
    (atlas) and 'l_' (light).
    """

    def __init__(self, a_color=(1., 1., 1.), a_opacity=1., a_template='B1',
                 a_projection='internal', a_hemisphere='both',
                 l_position=(100., 100., 100.), l_intensity=(1., 1., 1.),
                 l_color=(1., 1., 1., 1.), l_ambient=0.05,
                 l_specular=0.5, **kwargs):
        """Init."""
        # ________________ INPUTS ________________
        self.template = a_template
        self.hemisphere = a_hemisphere
        self.color = a_color
        self.opacity = a_opacity
        self.projection = a_projection
        self.sagittal, self.coronal, self.axial = (0, 0, 0)
        self.l_pos, self.l_int, self.l_col = l_position, l_intensity, l_color
        self.l_amb, self.l_spec = l_ambient, l_specular
        self._defcolor = (1., 1., 1.)
        self._scaleMax = 800.

        # ________________ PATH & TEMPLATES ________________
        # Find relative path to templates :
        dirfile = sys.modules[__name__].__file__.split('Atlas')[0]
        self._surf_path = os.path.join(dirfile, 'templates')
        # Build list of templates available from the templates/ folder :
        self._surf_list = ['B1', 'B2', 'B3', 'roi']
        for k in os.listdir(self._surf_path):
            file, ext = os.path.splitext(k)
            if (ext == '.npz') and (file not in self._surf_list):
                self._surf_list.append(file)
        del self._surf_list[self._surf_list.index('roi')]

        # ________________ INITIALIZE ________________
        # Load template :
        vertices, faces, normals, lr_index = self._load_template(self.template)
        # Set Brain mesh :
        self.mesh = BrainMesh(vertices, faces, normals, a_hemisphere, lr_index,
                              l_position, l_color, l_intensity, l_ambient,
                              l_specular, self._scaleMax, name='Brain')
        self._nv = len(self.mesh)
        # Opacity :
        self.mask = np.zeros((len(self.mesh), 3), dtype=bool)
        self.mesh.set_alpha(self.opacity)
        self.mesh.projection(a_projection)

    def __len__(self):
        """Return the number of vertices."""
        return len(self.vert)

    def __iter__(self):
        """Iteration over vertices."""
        for k in range(len(self)):
            yield self.vert[k, ...]

    def __del__(self):
        """Delete brain mesh."""
        self.mesh.clean()

    def _load_template(self, template='B1'):
        """Load the atlas to use for the interface.

        Use either a default or a custom template using the vertices and
        faces inputs.

        Parameters
        ----------
        template : string | 'B1'
            The template to import. Use either 'B1', 'B2' or 'B3'.

        Returns
        -------
        vertices : array_like
            Vertices to set of shape (M, 3, 3)
        faces : array_like
            Faces to set of shape (M, 3)
        normals : array_like
            Normals per faces (needed for light) of shape (M, 3, 3)
        lr_index : int
            Index at which to split Left and Right hemisphere.
        """
        if template not in self._surf_list:
            warn("No template " + template + ". B1 used instead.")
            self.template = template = 'B1'
        # Load a default template :
        atlas = np.load(os.path.join(self._surf_path, template + '.npz'))
        # Get Left/Right index :
        lr_index = atlas['lr_index'] if 'lr_index' in atlas.keys() else None
        return atlas['vertices'], atlas['faces'], atlas['normals'], lr_index

    def set_data(self, template=None, hemisphere=None):
        """Set template and hemisphere.

        Parameters
        ----------
        template : string
            Name of the template to use.
        hemisphere : {'both', 'right', 'left'}
            Hemisphere to use.
        """
        # ______________________ TEMPLATE ______________________
        vertices, faces, normals, lr_index = self._load_template(template)
        self.template = template

        # ______________________ HEMISPHERE ______________________
        self.hemisphere = hemisphere
        self.mesh.set_data(vertices, faces, normals, hemisphere, lr_index)

        # ______________________ VARIABLES ______________________
        self._nv = len(self.mesh)
        self.mask = np.zeros((len(self.mesh), 3), dtype=bool)
