import numpy as np
import os
from warnings import warn

import vispy.scene.visuals as visu

import visbrain
from ..utils import array2colormap, normalize


__all__ = ['ConnectivityBase']



class ConnectivityBase(object):

    """Class for connectivity
    """

    def __init__(self, canvas, **kwargs):
        self.canvas = canvas
        self.xyz = kwargs['c_xyz']
        self.connect = kwargs['c_connect']
        self.select = kwargs['c_select']
        self.colorby = kwargs['c_colorby']
        self.radiusmin = kwargs['c_radiusmin']
        self.radiusmax = kwargs['c_radiusmax']
        self.transform = kwargs['c_transform']
        self.cmap = kwargs['cmap']

        if (self.xyz is not None) and (self.connect is not None):
            self.prepare2plot()
            self.select2plot()
            self.plot()

    def __len__(self):
        return np.array(np.where(~self.connect.mask)).T

    def prepare2plot(self):
        """
        """
        # 
        self.xyz = self.transform.map(self.xyz)[:, 0:-1]
        N = self.xyz.shape[0]
        # Chech array :
        if (self.connect.shape != (N, N)) or not isinstance(self.connect, np.ndarray):
            raise ValueError('c_connect must be an array of shape '+str((N, N)))
        if self.select is None:
            self.select = np.ones_like(self.connect)
        if (self.select.shape != (N, N) or not isinstance(self.select, np.ndarray)):
            raise ValueError('c_select must be an array of shape '+str((N, N)))
        # Mask c_connect :
        try:
            self.connect.mask
        except:
            self.connect = np.ma.masked_array(self.connect, mask=True)
        self.connect.mask[self.select.nonzero()] = False

    def select2plot(self):
        """
        """
        self.to_plot = np.array(np.where(~self.connect.mask)).T

    def plot(self):
        """
        """
        if self.colorby == 'count':
            X = self.connect.count(1)
            cmap = array2colormap(self.connect.count(1), cmap=self.cmap)
            cmap[:, 3] = normalize(X, tomin=0.1, tomax=1)
            self.mesh = visu.Line(pos=self.xyz, color=cmap, connect=self.to_plot, width=self.radiusmin, method='gl')
            self.canvas.add(self.mesh)
        elif self.colorby == 'strength':
            x = self.connect.compressed()
            cmap = array2colormap(x, cmap=self.cmap)
            cmap[:, 3] = normalize(x, tomin=0.2, tomax=1)
            radius = normalize(x, tomin=self.radiusmin, tomax=self.radiusmax)
            lines = []
            for i in range(len(self.to_plot)):
                line = visu.Line(pos=self.xyz[self.to_plot[i, :], :], color=cmap[i, :], width=radius[i], method='gl', parent=self.canvas.scene)
                lines.append(line)

        # z0 = np.where(np.abs(self.vert[:, 2]) == np.abs(self.vert[:, 2]).min())[0]
        # newmesh = np.zeros_like(self.vert[:, 0:2])
        # newmesh[:, 0:2] = self.vert[:, 0:2]
        # self.mesh2 = visu.Line(pos=self.transform.map(newmesh)[:, 0:3], color=(0.9,0.9,0.9,0.1), width=3, method='gl')
        # self.canvas.add(self.mesh2)



