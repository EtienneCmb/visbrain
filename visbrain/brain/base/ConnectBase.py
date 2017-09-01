"""Base class for connectivity.

- Create a connectivity object (ConnectMesh)
- colormap managment for connectivity
"""
import numpy as np
from scipy.interpolate import splprep, splev
from collections import Counter
from warnings import warn

import vispy.scene.visuals as visu

from ...utils import color2vb, array2colormap, normalize
from ...visuals import CbarArgs


__all__ = ['ConnectBase']


class ConnectBase(CbarArgs):
    """Base class for connecivity managment.

    From all inputs arguments, this class use only those containing 'c_'
    (connectivity).
    """

    def __init__(self, _xyz=[], c_xyz=None, c_connect=None, c_select=None,
                 c_colorby='strength', c_dynamic=None, c_cmap='viridis',
                 c_vmin=None, c_vmax=None, c_colval=None,
                 c_under=None, c_over=None, c_clim=(0., 1.),
                 c_linewidth=3., c_dradius=30., c_blxyz=.1, c_blradius=13.,
                 c_bundling=False, **kwargs):
        """Init."""
        # Initialize elements :
        if (_xyz is not None) and(c_xyz is None):
            warn("No node's coordinates found for connectivity (c_xyz). "
                 "Source's location will be used instead")
        # Connectivity properties :
            self.xyz = _xyz
        else:
            self.xyz = c_xyz
        self.connect = c_connect
        self.select = c_select
        self._lw = c_linewidth
        self.needupdate = True
        # Color :
        self.colorby = c_colorby
        self.dynamic = c_dynamic
        self.colval = c_colval
        # Density :
        self.dradius = c_dradius
        # Bundling :
        self.bl = c_bundling
        self.blradius = c_blradius
        self.blxyz = c_blxyz
        self.blinterp = 100

        # Initialize colormap :
        isvmin, isvmax = c_vmin is not None, c_vmax is not None
        CbarArgs.__init__(self, c_cmap, c_clim, isvmin, c_vmin, isvmax, c_vmax,
                          c_under, c_over)

        # Object creation :
        if (self.xyz is not None) and (self.connect is not None):
            self.mesh = visu.Line(name='Connectivity', antialias=False)
            self.mesh.set_gl_state('translucent')
            self.update()
            self._maskbck = self.connect.mask.copy()
        else:
            self.mesh = visu.Line(name='NoneConnect')

    def __len__(self):
        """Return the number of sources."""
        return self.xyz.shape[0]

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
        if self.colorby not in ['count', 'strength', 'density']:
            raise ValueError("The c_colorby parameter must be 'count', "
                             "'strength' or 'density'")
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
        """Check color variables."""
        # ================== COLOR TYPE ==================
        # ----------- Strength -----------
        if self.colorby == 'strength':
            # Get non-zeros-values :
            nnz_values = self.connect.compressed()
            # Concatenate in alternance all non-zero values :
            self._all_nnz = np.c_[nnz_values, nnz_values].flatten()

        # ----------- Count -----------
        elif self.colorby == 'count':
            # Count the number of occurence for each node :
            node_count = Counter(np.ravel([self._nnz_x, self._nnz_y]))
            self._all_nnz = np.array([node_count[k] for k in self._indices])

        # ----------- density -----------
        elif self.colorby == 'density':
            # Get center to center distance :
            center, diff = self._center_distance()
            # Wind where distances are under density radius :
            d = np.ravel(np.where(diff <= self.dradius))
            # Start coloring :
            self._all_nnz = np.zeros((self.a_position.shape[0],),
                                     dtype=np.float32)
            for num, k in enumerate(np.unique(d)):
                dxk = np.array(np.where(d == k)[0])
                self._all_nnz[2 * d[dxk]] = len(dxk)
                self._all_nnz[2 * d[dxk] + 1] = len(dxk)

        # ================== MinMax ==================
        # Get (min / max) :
        self._minmax = (self._all_nnz.min(), self._all_nnz.max())
        if self.needupdate:
            self._clim = self._minmax

        # ================== GET COLOR ==================
        # ----------- User specific color -----------
        if (self.colval is not None) and isinstance(self.colval, dict):
            # Build a_color and send to buffer :
            self.a_color = np.zeros((2*len(self._nnz_x), 4), dtype=np.float32)
            for k, v in zip(self.colval.keys(), self.colval.values()):
                self.a_color[self._all_nnz == k, :] = v

        # ----------- Colormap -----------
        else:
            colormap = array2colormap(self._all_nnz, cmap=self._cmap,
                                      vmin=self._vmin,
                                      vmax=self._vmax,
                                      under=self._under,
                                      over=self._over,
                                      clim=self._clim)

            # Dynamic alpha :
            if (self.dynamic is not False) and isinstance(self.dynamic, tuple):
                colormap[:, 3] = normalize(self._all_nnz,
                                           tomin=self.dynamic[0],
                                           tomax=self.dynamic[1])

            # Build a_color and send to buffer :
            self.a_color = np.zeros((2*len(self._nnz_x), 4), dtype=np.float32)
            self.a_color[self._Nindices, :] = colormap[self._Nindices, :]

        # Set to data :
        if self.bl:
            self.bundling()
        else:
            self.mesh.set_data(pos=self.a_position, color=self.a_color,
                               connect='segments', width=self.lw)
        self.needupdate = False

    def _center_distance(self):
        """Get the euclidian distance between centers."""
        # Split positions in segments of two points :
        cut = np.vsplit(self.a_position, int(self.a_position.shape[0]/2))
        # Get center position and starting line position :
        center = np.mean(cut, axis=1)

        # ============ EUCLIDIAN DISTANCE ============
        diff = np.sqrt(np.square(center[:, np.newaxis, :] - center).sum(2))
        diff[np.tril_indices_from(diff)] = np.inf

        return center, diff

    def bundling(self):
        sh = self.a_position.shape
        pos = self.a_position
        # Split positions in segments of two points :
        cut = np.vsplit(pos, int(sh[0]/2))
        # Get center position and starting line position :
        center = np.mean(cut, axis=1)

        # ============ EUCLIDIAN DISTANCE ============
        diff = np.sqrt(np.square(center[:, np.newaxis, :] - center).sum(2))
        diff[np.tril_indices_from(diff)] = np.inf

        # ============ PROXIMAL LINES ============
        dx, dy = np.where(diff <= self.blradius)
        r = np.arange(len(center))
        for k in np.unique(dx):
            dk = dx == k
            c = center[[k] + list(r[dy[dk]]), :].mean(0)
            center[k, :] += (c - center[k, :]) * self.blxyz
            center[dy[dk], :] += (c - center[dy[dk], :]) * self.blxyz

        # ============ 3rd POINT IN THE MIDDLE ============
        col = self.a_color[0::2, :]
        pos = np.c_[pos[0::2], center, pos[1::2]].reshape(len(center)*3, 3)

        cut = np.vsplit(pos, int(pos.shape[0]/3))

        pos = np.array([])
        color = np.array([])
        index = np.arange(self.blinterp)
        idx = np.c_[index[:-1], index[1:]].flatten()
        for num, k in enumerate(cut):
            tckp, u = splprep(np.ndarray.tolist(k.T), k=2, s=0.)
            y2 = np.array(splev(np.linspace(0, 1, self.blinterp), tckp)).T[idx]
            pos = np.vstack((pos, y2)) if pos.size else y2
            colrep = np.tile(col[[num], ...], (len(y2), 1))
            color = np.vstack((color, colrep)) if color.size else colrep

        self.mesh.set_data(pos=pos, color=color)

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

    # ----------- NAME -----------
    @property
    def name(self):
        """Get the name value."""
        return self.mesh.name
