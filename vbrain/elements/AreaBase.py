import numpy as np
import warnings
import os

import numpy as np
from vispy import app, visuals, scene
from vispy.geometry.isosurface import isosurface
import vispy.visuals.transforms as vist

from visbrain.vbrain.utils import *
from visbrain.vbrain.visuals import BrainMesh
import visbrain

# warnings.filterwarnings('ignore', r'with ndim')
__all__ = ['AreaBase']



class AreaBase(object):

    """docstring for AreaBase
    """

    def __init__(self, structure='brod', select=None, color='white', cmap=None, scale_factor=1,
                 name='', transform=None):
        self.atlaspath = os.path.dirname(visbrain.__file__)+'/vbrain/elements/templates/'
        self.file = 'AAL_label.npz'
        self._structure = structure
        self._select = select
        self._selectAll = True
        self._unicolor = True
        self._color = color
        self.cmap = cmap
        self._scale_factor = scale_factor
        self._name = name
        self.mesh = None

        if transform is not None:
            self._transform = transform
        


    def _load(self):
        """
        """
        # Load the atlas :
        atlas = np.load(self.atlaspath+self.file)

        # Manage atlas :
        if self._structure not in ['aal', 'brod']:
            raise ValueError("structure must be either 'aal' or 'brod'")
        else:
            if self._structure == 'aal':
                self._vol = atlas['vol']
                self._idx = atlas['vol']
                self._uidx = np.unique(atlas['aal_idx'])
                label_L = np.array(["%.2d" % (num+1)+': '+k+' (L)' for num, k in zip(np.arange(0, len(atlas['aal_label'])*2, 2),
                                                                             atlas['aal_label'])])
                label_R = np.array(["%.2d" % (num+1)+': '+k + ' (R)' for num, k in zip(np.arange(1, len(atlas['aal_label'])*2 + 1, 2),
                                                                               atlas['aal_label'])])
                self._label = np.column_stack((label_L, label_R)).flatten()
            elif self._structure == 'brod':
                self._vol = atlas['brod_idx']
                self._idx = atlas['brod_idx']
                self._uidx = np.unique(self._vol)[1::]
                self._label = np.array(["%.2d" % k +': BA'+str(k) for num, k in enumerate(self._uidx)])



    def _preprocess(self):
        """
        """
        # Manage select :
        if self._select is None:
            self._select = self._uidx
            self._selectAll = True
        elif not isinstance(self._select, list):
            self._select = list(self._select)
            self._selectAll = False
        else:
            self._selectAll = False
        for k in self._select:
            if k not in self._uidx:
                raise ValueError(str(k)+' not in :', self._uidx)

        # Manage color :
        if not isinstance(self._color, list) and isinstance(self._color, str):
            self._color = list([self._color])
            self._unicolor = True
        else:
            self._unicolor = False
        if len(self._color) != len(self._select):
            self._color = [self._color[0]]*len(self._select)
            self._unicolor = True
        else:
            self._unicolor = False
        if self.cmap is not None:
            self._color = array2colormap(np.arange(len(self._select)), cmap=self.cmap)
            self._color = [tuple(self._color[k, :]) for k in range(self._color.shape[0])]
            self._unicolor = False
            self._selectAll = False

        self._selectedIndex = [np.argwhere(self._uidx == k)[0][0] for k in self._select]
        self._selectedLabels = self._label[self._selectedIndex]
        self._color = [color2vb(k) for k in self._color]
        self._color_idx ,self.vertex_colors = np.array([]), np.array([])


    def _get_vertices(self):
        """
        """
        # Pre-load atlas :
        vertemp = isosurface(self._vol, level=0.5)[0]
        xm, ym, zm = vertemp[:, 0].mean(), vertemp[:, 1].mean(), vertemp[:, 2].mean()

        # Select all and unicolor :
        if self._selectAll and self._unicolor:
            self.vert, self.faces = isosurface(self._vol, level=0.5)
            self.vertex_colors = color2faces(self._color[0], self.faces.shape[0])
            self._color_idx = np.zeros((self.faces.shape[0],))

        # Don't select all but unicolor :
        elif not self._selectAll and self._unicolor:
            # Select areas :
            vol = np.ma.masked_array(self._vol.copy(), mask=False)
            for k in self._select:
                vol.mask[self._idx == k] = True
            # Get vertices/faces for all areas :
            self._vol[~vol.mask] = 0
            self.vert, self.faces = isosurface(self._vol, level=np.array(self._select).min())
            self.vertex_colors = color2faces(self._color[0], self.faces.shape[0])
            self._color_idx = np.zeros((self.faces.shape[0],))

        # Select specific andspecific colors :
        elif not self._selectAll and not self._unicolor:
            self.vert, self.faces = np.array([]), np.array([])
            q = 0
            for num, k in enumerate(self._select):
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
                idxT = np.full((facesT.shape[0],), k, dtype=np.int64)
                self._color_idx = np.concatenate((self._color_idx, idxT)) if self._color_idx.size else idxT
                color = color2faces(self._color[num], facesT.shape[0])
                self.vertex_colors = np.concatenate((self.vertex_colors, color)) if self.vertex_colors.size else color
                # Update maximum :
                q = self.faces.max()

        # Other case :
        else:
            raise ValueError('Error: cannot match between color and areas to select')

        # Finally, apply transformation to vertices :
        self.vert[:, 0] -= xm
        self.vert[:, 1] -= ym
        self.vert[:, 2] -= zm
        # self.vert = self._transform.map(self.vert)[:, 0:-1]

    def _plot(self):
        """
        """
        self.mesh = BrainMesh(vertices=self.vert, faces=self.faces, vertex_colors=self.vertex_colors,
                              scale_factor=self._scale_factor, name=self._name, recenter=False)


    def _get_index(self, index):
        """
        """
        # Get list of unique index :
        uindex = np.unique(self._color_idx)
        # Create an empty mask :
        mask = np.zeros((len(self._color_idx),), dtype=bool)
        # Convert index :
        if index is None:
            index = list(uindex)
        if not isinstance(index, list):
            index = [index]
        # Check if index exist :
        for k in index:
            if k not in uindex:
                warnings.warn(str(k)+' not found in the list of existing areas')
            else:
                mask[self._color_idx == k] = True
        return mask


    def set_alpha(self, alpha, index=None):
        """
        """
        # Get corresponding index of areas :
        mask = self._get_index(index)
        # Set alpha :
        self.mesh.set_alpha(alpha, index=np.tile(mask[:, np.newaxis], (1, 3)))


    def set_color(self, color, index=None):
        """
        """
        # Get corresponding index of areas :
        mask = self._get_index(index)
        # Get RGBA color :
        color = color2vb(color)
        # Convert
        # Set color to vertex color :
        self.vertex_colors[mask, ...] = color
        self.mesh.set_color(self.vertex_colors)
        self.mesh.update()

    def set_camera(self, camera):
        """
        """
        self.mesh.set_camera(camera)

    @property
    def structure(self):
        return self._structure

    @structure.setter
    def structure(self, value):
        self._structure = value
        self._load()

    @property
    def select(self):
        return self._select

    @select.setter
    def select(self, value):
        self._select = value
        self._load()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._load()

