"""Base class for connectivity.

- Create a connectivity object (Connect)
- colormap managment for connectivity
"""

import vispy.scene.visuals as visu

from ..utils import _colormap
from ..visuals import Connect


__all__ = ['ConnectivityBase']


class ConnectivityBase(_colormap):
    """Base class for connecivity managment.

    From all inputs arguments, this class use only those containing 'c_'
    (connectivity).
    """

    def __init__(self, c_xyz=[], c_connect=None, c_select=None,
                 c_colorby='count', c_transform=[], c_dynamic=None,
                 c_cmap='viridis', c_cmap_vmin=None, c_cmap_vmax=None,
                 c_cmap_under=None, c_cmap_over=None, c_cmap_clim=None,
                 **kwargs):
        """Init."""
        # Initialize elements :
        self.xyz = c_xyz
        self.connect = c_connect
        self.select = c_select
        self.colorby = c_colorby
        self.transform = c_transform
        self.dynamic = c_dynamic

        # Initialize colormap :
        _colormap.__init__(self, c_cmap, c_cmap_clim, c_cmap_vmin, c_cmap_vmax,
                           c_cmap_under, c_cmap_over, c_connect)

        # Object creation :
        if (self.xyz is not None) and (self.connect is not None):
            self.mesh = Connect(self.xyz, self.connect, select=self.select,
                                colorby=self.colorby, dynamic=self.dynamic,
                                name='Connectivity', **self._cb)
            self._maskbck = self.mesh.connect.mask.copy()
        else:
            self.mesh = visu.Line(name='NoneConnect')
