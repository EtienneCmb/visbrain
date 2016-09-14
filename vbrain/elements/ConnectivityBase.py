import numpy as np
import os
from warnings import warn

import vispy.scene.visuals as visu
from vispy.scene import Node

import visbrain
from ..utils import array2colormap, normalize
from ..visuals import Connect


__all__ = ['ConnectivityBase']



class ConnectivityBase(object):

    """Class for connectivityd
    """

    def __init__(self, c_xyz=[], c_connect=None, c_select=None, c_colorby='count',
                 c_transform=[], cmap='viridis', c_dynamic=True, **kwargs):
        self.xyz = c_xyz
        self.connect = c_connect
        self.select = c_select
        self.colorby = c_colorby
        self.transform = c_transform
        self.cmap = cmap

        if (self.xyz is not None) and (self.connect is not None):
            self.mesh = Connect(self.xyz, self.connect, select=self.select, colorby=self.colorby,
                                cmap=self.cmap, dynamic=c_dynamic, name='Connectivity')
            self._maskbck = self.mesh.connect.mask.copy()
        else:
            self.mesh = visu.Line(name='Connectivity')

