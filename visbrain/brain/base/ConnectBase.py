"""Base class for connectivity.

- Create a connectivity object (ConnectMesh)
- colormap managment for connectivity
"""
import numpy as np
from collections import Counter

import vispy.scene.visuals as visu

# from .visuals import ConnectMesh
from ...utils import _colormap, color2vb, array2colormap, normalize


__all__ = ['ConnectBase']


class ConnectBase(_colormap):
    """Base class for connecivity managment.

    From all inputs arguments, this class use only those containing 'c_'
    (connectivity).
    """

    def __init__(self, c_xyz=[], c_connect=None, c_select=None,
                 c_colorby='strength', c_dynamic=None, c_cmap='viridis',
                 c_cmap_vmin=None, c_cmap_vmax=None, c_colval=None,
                 c_cmap_under=None, c_cmap_over=None, c_cmap_clim=None,
                 c_linewidth=3., **kwargs):
        """Init."""
        # Initialize elements :
        self.xyz = c_xyz
        self.connect = c_connect
        self.select = c_select
        self.colorby = c_colorby
        self.dynamic = c_dynamic
        self.colval = c_colval
        self._lw = c_linewidth

        # Initialize colormap :
        _colormap.__init__(self, c_cmap, c_cmap_clim, c_cmap_vmin, c_cmap_vmax,
                           c_cmap_under, c_cmap_over, c_connect)

        # Object creation :
        if (self.xyz is not None) and (self.connect is not None):
            self.mesh = visu.Line(name='Connectivity', antialias=True)
            self.mesh.set_gl_state('translucent', depth_test=True)
            self.update()
        else:
            self.mesh = visu.Line(name='NoneConnect')

    def _check_data(self):
        """Check data and color."""
        # ================ CHECK DATA / CONNECT / SELECT ================
        N = self.xyz.shape[0]
        # Chech array :
        if (self.connect.shape != (N, N)) or not isinstance(self.connect,
                                                            np.ndarray):
            raise ValueError("c_connect must be an array of "
                             "shape " + str((N, N)))
        if self.select is None:
            self.select = np.ones_like(self.connect)
        if (self.select.shape != (N, N) or not isinstance(self.select,
                                                          np.ndarray)):
            raise ValueError("c_select must be an array of "
                             "shape " + str((N, N)))
        # Mask c_connect :
        try:
            self.connect.mask
        except:
            self.connect = np.ma.masked_array(self.connect, mask=True)
        self.connect.mask[self.select.nonzero()] = False
        # Use specific color values :
        if (self.colval is not None) and isinstance(self.colval, dict):
            mask = np.ones_like(self.connect.mask)
            for k, v in zip(self.colval.keys(), self.colval.values()):
                mask[self.connect.data == k] = False
                self.colval[k] = color2vb(v)
            self.connect.mask = mask

        # ================ CHECK COLOR ================
        # Check colorby :
        if self.colorby not in ['count', 'strength']:
            raise ValueError("The c_colorby parameter must be 'count' or "
                             "'strength'")
        # Test dynamic :
        if (self.dynamic is not None) and not isinstance(self.dynamic, tuple):
            raise ValueError("c_dynamic bust be a tuple")

        # ================ NON-ZERO INDICES ================
        # Find where there is non-masked connections :
        self._nnz_x, self._nnz_y = np.where(~self.connect.mask)
        self._indices = np.c_[self._nnz_x, self._nnz_y].flatten()
        self._Nindices = np.arange(len(self._indices))
        # Build position array :
        self.a_position = np.zeros((2*len(self._nnz_x), 3), dtype=np.float32)
        self.a_position[self._Nindices, :] = self.xyz[self._indices, :]

    def _check_color(self):
        """
        """
        # Colorby strength of connection :
        if self.colorby == 'strength':
            # Get non-zeros-values :
            nnz_values = self.connect.compressed()
            # Concatenate in alternance all non-zero values :
            self._all_nnz = np.c_[nnz_values, nnz_values].flatten()
            # Get looping indices :
            self._loopIndex = self._Nindices

        # Colorby count on each node :
        elif self.colorby == 'count':
            # Count the number of occurence for each node :
            node_count = Counter(np.ravel([self._nnz_x, self._nnz_y]))
            self._all_nnz = np.array([node_count[k] for k in self._indices])
            # Get looping indices :
            self._loopIndex = self._Nindices

        # Get (min / max) :
        self._MinMax = (self._all_nnz.min(), self._all_nnz.max())
        if self._cb['clim'] is None:
            self._cb['clim'] = self._MinMax

        # Get associated colormap :
        if (self.colval is not None) and isinstance(self.colval, dict):
            # Build a_color and send to buffer :
            self.a_color = np.zeros((2*len(self._nnz_x), 4), dtype=np.float32)
            for k, v in zip(self.colval.keys(), self.colval.values()):
                self.a_color[self._all_nnz == k, :] = v
        else:
            colormap = array2colormap(self._all_nnz, cmap=self._cb['cmap'],
                                      vmin=self._cb['vmin'],
                                      vmax=self._cb['vmax'],
                                      under=self._cb['under'],
                                      over=self._cb['over'],
                                      clim=self._cb['clim'])

            # Dynamic alpha :
            if (self.dynamic is not False) and isinstance(self.dynamic, tuple):
                colormap[:, 3] = normalize(self._all_nnz,
                                           tomin=self.dynamic[0],
                                           tomax=self.dynamic[1])

            # Build a_color and send to buffer :
            self.a_color = np.zeros((2*len(self._nnz_x), 4), dtype=np.float32)
            self.a_color[self._Nindices, :] = colormap[self._loopIndex, :]

        # Set to data :
        self.mesh.set_data(pos=self.a_position, color=self.a_color,
                           connect='segments', width=self.lw)

    def update(self):
        """Update."""
        self._check_data()
        self._check_color()


    # ----------- LW -----------
    @property
    def lw(self):
        """Get the lw value."""
        return self._lw

    @lw.setter
    def lw(self, value):
        """Set lw value."""
        self.mesh.set_data(width=value)
