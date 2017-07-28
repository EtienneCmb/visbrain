"""Desc."""

import numpy as np

import vispy.scene.visuals as visu
from ...utils import normalize, color2vb

__all__ = ('TimeSeriesBase')


class TimeSeriesBase(object):
    """Add and configure time-series.

    From all inputs arguments, this class use only those containing 'ts_'
    (time-series).
    """

    def __init__(self, ts_xyz=None, ts_data=None, ts_color='white', ts_amp=6.,
                 ts_width=20., ts_lw=1.5, ts_dxyz=(0., 0., 1.), **kwargs):
        """Init."""
        self.xyz = ts_xyz
        self.data = ts_data
        self.color = color2vb(ts_color)
        self.amp = ts_amp
        self.width = ts_width
        self.lw = ts_lw
        self.dxyz = ts_dxyz

        self.mesh = visu.Line(name='NoneTimeSeries')
        if (ts_xyz is not None) and (ts_data is not None):
            self._data2xyz()
            self.mesh.name = 'TimeSeries'

    def _data2xyz(self):
        """Turn the data into (x, y, y) line."""
        # Get the number of sources :
        nsources = self.xyz.shape[0]
        # Check if the data have the correct shape :
        if self.data.shape[0] != nsources:
            raise ValueError("The shape of the time-series must be (n_sources,"
                             " n_time_points)")
        else:
            npts = self.data.shape[1]
        # Build the position vector :
        pos = np.zeros((nsources, npts, 3), dtype=np.float32)
        time = np.linspace(-self.width / 2, self.width / 2, npts)
        data = normalize(self.data, -self.amp / 2, self.amp / 2)
        for k in range(nsources):
            pos[k, :, 0] = self.xyz[k, 0] + time + self.dxyz[0]
            pos[k, :, 1] = self.xyz[k, 1] + data[k, :] + self.dxyz[1]
            pos[k, :, 2] = self.xyz[k, 2] + self.dxyz[2]
        pos = pos.reshape(nsources * npts, 3)
        # Build the connection vector :
        if not np.ma.is_masked(self.data):
            connect = np.ones((nsources, npts), dtype=bool)
        else:
            connect = ~ self.data.mask
        connect[:, -1] = False
        self.mesh.set_data(pos=pos, color=self.color, connect=connect.ravel(),
                           width=self.lw)

    def set_data(self, color=None, lw=None, amp=None, width=None, dxyz=None,
                 visible=True):
        needupdate = False
        if amp is not None:
            self.amp = amp
            needupdate = True
        if width is not None:
            self.width = width
            needupdate = True
        if dxyz is not None:
            self.dxyz = dxyz
            needupdate = True
        if color is not None:
            self.color = color
        if lw is not None:
            self.lw = lw

        if needupdate:
            self._data2xyz()
        self.mesh.visible = visible
