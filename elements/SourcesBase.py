import numpy as np
import os
from warnings import warn

import vispy.scene.visuals as visu

from ..utils import color2vb, normalize

__all__ = ['SourcesBase']


class SourcesBase(object):

    """Class for sources creation
    """

    def __init__(self, canvas, **kwargs):
        # Initialize elements :
        self.canvas = canvas
        self.xyz = kwargs['s_xyz']
        self.data = kwargs['s_data']
        self.color = kwargs['s_color']
        self.alpha = kwargs['s_alpha']
        self.scaling = kwargs['s_scaling']
        self.transform = kwargs['s_transform']
        self.radiusmin = kwargs['s_radiusmin']*1.5
        self.radiusmax = kwargs['s_radiusmax']*1.5
        self._defcolor = 'slateblue'
        self._rescale = 3.0
        self.shading = 'smooth'

        # Plot :
        if self.xyz is not None:
            self.prepare2plot()
            self.plot()

    def __len__(self):
        return len(np.where(self.data.mask == False)[0])

    def __iter__(self):
        for k in range(len(self)):
            yield np.ravel(self.xyz[k, :])

    def __get__(self, instance, owner):
        return self.xyz


    def prepare2plot(self):
        """Prepare data before plotting
        """      
        # --------------------------------------------------------------------
        # Check xyz :
        self.xyz = np.array(self.xyz)
        if self.xyz.ndim is not 2:
            self.xyz = self.xyz[:, np.newaxis]
        if 3 not in self.xyz.shape:
            raise ValueError("xyz must be an array of size (N, 3)")
        elif self.xyz.shape[1] is not 3:
            self.xyz = self.xyz.T
        self.xyz = self.xyz
        self.nSources = self.xyz.shape[0]
        # Apply transformation to coordinates :
        self.xyz = self.transform.map(self.xyz)[:, 0:-1]

        # --------------------------------------------------------------------
        # Check color :
        if isinstance(self.color, str): # simple string
            self.sColor = color2vb(color=self.color, default=self.color,
                                   length=self.nSources, alpha=self.alpha)
        elif isinstance(self.color, list): # list of colors
            if len(self.color) != self.nSources:
                raise ValueError("The length of the color sources list must "
                                 "be the same the number of electrode.")
            else:
                self.sColor = np.squeeze(np.array([color2vb(color=k, length=1, alpha=self.alpha) for k in self.color]))
                if (self.sColor.shape[1] is not 4): self.sColor = self.sColor.T
        elif isinstance(self.color, np.ndarray): # array of colors
            if nSource not in self.color.shape:
                raise ValueError("color for sources must be a (N, 3) array (for rgb) "
                                 "or (N, 4) for rgba.")
            else:
                if (self.color.shape[1] is not 4): self.color = self.color.T
                self.sColor = self.color

        # --------------------------------------------------------------------
        # Check radius :
        if not isinstance(self.radiusmin, (int, float)):
            raise ValueError("s_radiusmin must be an integer or a float number.")
        if not isinstance(self.radiusmax, (int, float)):
            raise ValueError("s_radiusmax must be an integer or a float number.")

        # --------------------------------------------------------------------
        # Check data :
        if self.data is None:
            self.data = np.ones((self.nSources,), dtype=float)
        try:
            self.data.mask
        except:
            self.data = np.ma.masked_array(np.ravel(self.data), mask=False)
        if len(self.data) != self.nSources:
            raise ValueError("The length of data must be the same as the number of electrodes")
        else:
            self.sData = self.array2radius(self.data.data, vmin=self.radiusmin, vmax=self.radiusmax, rescale=self.scaling)


    def array2radius(self, data, vmin=0.02, vmax=0.05, rescale=True):
        """Transform an array of data to source's radius
        """
        # Constant data :
        if np.unique(data).size == 1:
            radius = vmin*np.ones((len(data),))
        # Non-constant values :
        else:
            radius = normalize(data, tomin=vmin, tomax=vmax)
        # Rescale data :
        if rescale: radius /= self._rescale
        return radius


    def plot(self):
        """Plot sources on the brain
        """
        # Find only unmasked data :
        xyz, sData, sColor = self._select_unmasked()
        # Render as cloud points :
        self.mesh = visu.Markers()
        self.mesh.set_data(xyz, edge_color=None, face_color=sColor, size=sData, scaling=self.scaling)
        # self.mesh.transform = self.transform
        self.canvas.add(self.mesh)


    def update(self):
        """Update sources plot
        """
        # Find only unmasked data :
        xyz, sData, sColor = self._select_unmasked()
        # Render as cloud points :
        if xyz.size:
            self.mesh.visible = True
            self.mesh.set_data(xyz, edge_color=None, face_color=sColor, size=sData, scaling=self.scaling)
            # self.mesh.transform = self.transform
        else:
            self.mesh.visible = False


    def _select_unmasked(self):
        """Select only unmasked sources
        """
        # Get unmasked data :
        mask = self.data.mask == False
        # Select unmasked sData and xyz :
        return self.xyz[mask, :], self.sData[mask], self.sColor[mask, :]


    def _reset_mask(self, reset_to=False):
        """
        """
        self.data.mask = reset_to