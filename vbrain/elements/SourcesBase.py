import numpy as np
import os
from warnings import warn

import vispy.scene.visuals as visu
import vispy.visuals.transforms as vist

from ..utils import color2vb, normalize, _colormap

__all__ = ['SourcesBase']


class SourcesBase(_colormap):

    """Class for sources creation
    """

    def __init__(self, s_xyz=None, s_data=None, s_color='#ab4652', s_radius=0.1, s_opacity=1.0, s_radiusmin=5.0,
                 s_radiusmax=10.0, s_edgecolor=None, s_edgewidth=0.6, s_scaling=False, s_transform=[],
                 s_text=None, s_textcolor='black', s_textsize=3, s_textshift=(0,2,0), s_mask=None, s_maskcolor='gray',
                 s_cmap='inferno', s_cmap_vmin=None, s_cmap_vmax=None, s_cmap_under=None, s_cmap_over=None,
                 s_projecton='surface', **kwargs):
        # Initialize elements :
        self.xyz = s_xyz
        self.data = s_data
        self.color = s_color
        self.edgecolor = color2vb(s_edgecolor)
        self.edgewidth = s_edgewidth
        self.alpha = s_opacity
        self.scaling = s_scaling
        self.transform = s_transform
        self.radiusmin = s_radiusmin*1.5
        self.radiusmax = s_radiusmax*1.5
        self._defcolor = 'slateblue'
        self._rescale = 3.0
        self.shading = 'smooth'
        self.stext = s_text
        self.stextcolor = color2vb(s_textcolor)
        self.stextsize = s_textsize
        self.stextshift = s_textshift
        self.smask = s_mask
        self.smaskcolor = color2vb(s_maskcolor)
        self.projecton = s_projecton

        # Initialize colorbar elements :
        _colormap.__init__(self, s_cmap, s_cmap_vmin, s_cmap_vmax, s_cmap_under, s_cmap_over)

        # Plot :
        if self.xyz is not None:
            self.prepare2plot()
            self.plot()
            self.text_plot()
        else:
            self.mesh = visu.Markers(name='NoneSources')
            self.stextmesh = visu.Text(name='NoneText')

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

        # --------------------------------------------------------------------
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
        # Check mask :
        if self.smask is not None:
            if len(self.smask) != self.nSources:
                raise ValueError("The length of mask must be the same as the number of electrodes")
            elif (len(self.smask) == self.nSources) and (self.smask.dtype != bool):
                raise ValueError("The mask must be an array of boolean values")
            else:
                # Get the RGBA of mask color :
                self.sColor[self.smask, ...] = self.smaskcolor
        else:
            self.smask = np.zeros((self.nSources,), dtype=bool)

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

        # --------------------------------------------------------------------
        # Check text :
        if self.stext is not None:
            if len(self.stext) != len(self):
                raise ValueError("The length of text data must be the same as the number of electrodes")


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
        xyz, sData, sColor, _ = self._select_unmasked()
        # Render as cloud points :
        self.mesh = visu.Markers(name='Sources')
        self.mesh.set_data(xyz, edge_color=self.edgecolor, face_color=sColor, size=sData,
                           scaling=self.scaling, edge_width=self.edgewidth)
        # self.mesh.set_gl_state('translucent', depth_test=False, cull_face=True)


    def update(self):
        """Update sources plot
        """
        # Find only unmasked data :
        xyz, sData, sColor, _ = self._select_unmasked()
        # Render as cloud points :
        if xyz.size:
            self.mesh.visible = True
            self.mesh.set_data(xyz, edge_color=self.edgecolor, face_color=sColor, size=sData,
                               scaling=self.scaling, edge_width=self.edgewidth)
            # self.mesh.transform = self.transform
        else:
            self.mesh.visible = False


    def _select_unmasked(self):
        """Select only unmasked sources
        """
        # Get unmasked data :
        mask = self.data.mask == False
        # Select unmasked sData and xyz :
        return self.xyz[mask, :], self.sData[mask], self.sColor[mask, :], mask


    def _reset_mask(self, reset_to=False):
        """
        """
        self.data.mask = reset_to

    def text_plot(self):
        """Plot text for each source
        """
        if self.stext is not None:
            self.stextmesh = visu.Text(text=self.stext, color=self.stextcolor, font_size=self.stextsize,
                                       pos=self.xyz, bold=True, name='SourcesText')
            self.stextmesh.set_gl_state('translucent', depth_test=True)
            self.stextmesh.transform = vist.STTransform(translate=self.stextshift)
        else:
            self.stextmesh = visu.Text(name='NoneText')

    def text_update(self):
        """Update text elements
        """
        if self.stext is not None:
            idx = self._select_unmasked()[-1]
            text = np.array(self.stext)
            text[np.array(~idx, dtype=bool)] = ''
            self.stextmesh.font_size = self.stextsize
            self.stextmesh.color = self.stextcolor
            self.stextmesh.text = text
            self.stextmesh.update()
