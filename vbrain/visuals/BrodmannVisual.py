import numpy as np
from warnings import warn
import os

import numpy as np
from vispy import app, visuals, scene
from vispy.geometry.isosurface import isosurface

from visbrain.vbrain.utils import *
from visbrain.vbrain.visuals import BrainMesh
import visbrain


__all__ = ['BrodmannVisual']


#############################################################################
# path = '/home/etienne/anaconda3/lib/python3.5/site-packages/visbrain/vbrain/elements/templates/'
# file = 'AAL_label.npz'
# mat = np.load(path+file)
#############################################################################


class BrodmannBase(object):

    """docstring for BrodmannVisual
    """

    def __init__(self, structure='brod', select=None, color='white', cmap=None):
        self.structure = structure
        self.select = select
        self._selectAll = True
        self._unicolor = True
        self.atlaspath = os.path.dirname(visbrain.__file__)+'/vbrain/elements/templates/'
        self.file = 'AAL_label.npz'
        self.color = color
        self.cmap = cmap

        self._load()
        self._get_vertices()
        self._plot()
        

    def _load(self):
        """
        """
        # Load the atlas :
        atlas = np.load(self.atlaspath+self.file)

        # Manage atlas :
        if self.structure not in ['aal', 'brod']:
            raise ValueError("structure must be either 'aal' or 'brod'")
        else:
            if self.structure == 'aal':
                self._vol = atlas['vol']
                self._idx = atlas['vol']
                self._uidx = np.unique(atlas['aal_idx'])
                self._label = [k for k in atlas['aal_label']]
            elif self.structure == 'brod':
                self._vol = atlas['brod_idx']
                self._idx = atlas['brod_idx']
                self._uidx = np.unique(self._vol)
                self._label = [str(k) for k in self._uidx]

        # Manage color :
        if not isinstance(self.color, list) and isinstance(self.color, str):
            self.color = list([self.color])
            self._unicolor = True
        else:
            self._unicolor = False
        if len(self.color) != len(self.select):
            self.color = [self.color[0]]*len(self.select)
            self._unicolor = True
        else:
            self._unicolor = False
        if self.cmap is not None:
            self.color = array2colormap(np.arange(len(self.select)), cmap=self.cmap)
            self.color = [tuple(self.color[k, :]) for k in range(self.color.shape[0])]
            self._unicolor = False

        # Manage select :
        if self.select is None:
            self.select = self._uidx
            self._selectAll = True
        elif not isinstance(self.select, list):
            self.select = list([self.select])
            self._selectAll = False
        else:
            self._selectAll = False
        for k in self.select:
            if k not in self._uidx:
                raise ValueError(str(k)+' not in :', self._uidx)

        self.color = [color2vb(k) for k in self.color]
        self.color_idx ,self.vertex_colors = np.array([]), np.array([])


    def _get_vertices(self):
        """
        """
        # Select all and unicolor :
        if self._selectAll and self._unicolor:
            self.vert, self.faces = isosurface(self._vol, level=0.5)
            self.vertex_colors = color2faces(self.color[0], self.faces.shape[0])
            self.color_idx = np.zeros((self.faces.shape[0],))

        # Don't select all but unicolor :
        elif not self._selectAll and self._unicolor:
            # Select areas :
            vol = np.ma.masked_array(self._vol.copy(), mask=False)
            for k in self.select:
                vol.mask[self._idx == k] = True
            # Get vertices/faces for all areas :
            self._vol[~vol.mask] = 0
            self.vert, self.faces = isosurface(self._vol, level=np.array(self.select).min())
            self.vertex_colors = color2faces(self.color[0], self.faces.shape[0])
            self.color_idx = np.zeros((self.faces.shape[0],))

        # Select specific andspecific colors :
        elif not self._selectAll and not self._unicolor:
            self.vert, self.faces = np.array([]), np.array([])
            q = 0
            for num, k in enumerate(self.select):
                # Remove unecessary index :
                vol = self._vol.copy()
                vol[self._idx != k] = 0
                # Get vertices/faces for this structure :
                vertT, facesT = isosurface(vol, level=k)
                # Update faces index :
                facesT += (q+1)
                # Concatenate vertices/faces :
                self.vert = np.concatenate((self.vert, vertT)) if self.vert.size else vertT
                self.faces = np.concatenate((self.faces, facesT)) if self.faces.size else facesT
                # Update colors and index :
                idxT = np.full((facesT.shape[0],), num)
                self.color_idx = np.concatenate((self.color_idx, idxT)) if self.color_idx.size else idxT
                color = color2faces(self.color[num], facesT.shape[0])
                self.vertex_colors = np.concatenate((self.vertex_colors, color)) if self.vertex_colors.size else color
                # Update maximum :
                q = self.faces.max()

        # Other case :
        else:
            raise ValueError('Error: cannot match between color and areas to select')

    def _plot(self):
        """
        """
        self.mesh = BrainMesh(vertices=self.vert, faces=self.faces, vertex_colors=self.vertex_colors)





# Finally we will test the visual by displaying in a scene.

canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='w', size=(2000,1000))

# Add a ViewBox to let the user zoom/rotate
from vispy.scene.cameras import *
cam = TurntableCamera()
view = canvas.central_widget.add_view()
view.camera = cam
# view.camera.fov = 1.
view.camera.distance = 10
view.camera.azimuth = 0.
V = view.camera

e = BrodmannBase(select=[4, 6, 32, 40], structure='brod', cmap='viridis')
e.mesh.parent = view.scene
e.mesh.set_camera(cam)

axis = scene.visuals.XYZAxis(parent=view.scene)

# ..and optionally start the event loop
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        app.run()