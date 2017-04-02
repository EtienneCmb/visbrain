"""Base class for sources and text sources managment.

Sources are small deep / surface points. It can materialize intracranial
electrodes or EEG / MEG captor. Each source can have an associated activity
that can be then projected on the surface.

This class is responsible of creating and add some utility functions for
sources objects.
"""

import numpy as np

import vispy.scene.visuals as visu
import vispy.visuals.transforms as vist

from ...utils import color2vb, normalize, _colormap

__all__ = ['SourcesBase']


class SourcesBase(_colormap):
    """Initialize the source object and to add some necessary functions.

    This class can be used for like plotting, loading... Each source's input
    start with 's_'. Other arguments (**kwargs) are ignored. This class is also
    responsible for associated text of each source.
    """

    def __init__(self, s_xyz=None, s_data=None, s_color='#ab4652',
                 s_opacity=1.0, s_radiusmin=5.0, s_radiusmax=10.0,
                 s_edgecolor=None, s_edgewidth=0.6, s_scaling=False,
                 s_text=None, s_symbol='disc', s_textcolor='black',
                 s_textsize=3, s_textshift=(0, 2, 0), s_mask=None,
                 s_maskcolor='gray', s_cmap='inferno', s_cmap_clim=None,
                 s_cmap_vmin=None, s_cmap_vmax=None, s_cmap_under=None,
                 s_cmap_over=None, s_projecton='surface', **kwargs):
        """Init."""
        # Initialize elements :
        self.xyz = s_xyz
        self.data = s_data
        self.color = s_color
        self.edgecolor = color2vb(s_edgecolor)
        self.edgewidth = s_edgewidth
        self.alpha = s_opacity
        self.scaling = s_scaling
        self.radiusmin = s_radiusmin
        self.radiusmax = s_radiusmax
        self.symbol = s_symbol
        self.stext = s_text
        self.stextcolor = color2vb(s_textcolor)
        self.stextsize = s_textsize
        self.stextshift = s_textshift
        self.smask = s_mask
        self.smaskcolor = color2vb(s_maskcolor)
        self.projecton = s_projecton
        self._defcolor = 'slateblue'
        self._rescale = 3.0

        # Initialize colorbar elements :
        _colormap.__init__(self, s_cmap, s_cmap_clim, s_cmap_vmin, s_cmap_vmax,
                           s_cmap_under, s_cmap_over, self.data)

        # Plot :
        if self.xyz is not None:
            self.prepare2plot()
            self.plot()
            self.text_plot()
        else:
            self.mesh = visu.Markers(name='NoneSources')
            self.stextmesh = visu.Text(name='NoneText')

    def __len__(self):
        """Get the length of non-masked sources."""
        return len(np.where(np.logical_not(self.data.mask))[0])

    def __iter__(self):
        """Iterations over sources coordinates."""
        for k in range(len(self)):
            yield np.ravel(self.xyz[k, :])

    def __get__(self, instance, owner):
        """Get sources coordinates matrix."""
        return self.xyz

    def __bool__(self):
        """Return if there's masked sources."""
        return any(self.smask)

    ##########################################################################
    # DATA CHECKING
    ##########################################################################
    def prepare2plot(self):
        """Prepare data before plotting.

        This method check any inputs and raise an error if it's not
        compatible.
        """
        # ======================== Check coordinates ========================
        # Check xyz :
        self.xyz = np.array(self.xyz).astype(np.float32)
        if self.xyz.ndim is not 2:
            self.xyz = self.xyz[:, np.newaxis]
        if 3 not in self.xyz.shape:
            raise ValueError("xyz must be an array of size (N, 3)")
        elif self.xyz.shape[1] is not 3:
            self.xyz = self.xyz.T
        self.xyz = self.xyz
        self.nSources = self.xyz.shape[0]

        # ======================== Check color ========================
        # Simple string :
        if isinstance(self.color, str):
            self.sColor = color2vb(color=self.color, default=self.color,
                                   length=self.nSources, alpha=self.alpha)
        # list of colors :
        elif isinstance(self.color, list):
            if len(self.color) != self.nSources:
                raise ValueError("The length of the color sources list must "
                                 "be the same the number of electrode.")
            else:
                self.sColor = np.squeeze(np.array([color2vb(
                    color=k, length=1, alpha=self.alpha) for k in self.color]))
                if (self.sColor.shape[1] is not 4):
                    self.sColor = self.sColor.T
        # Array of colors :
        elif isinstance(self.color, np.ndarray):
            if self.nSource not in self.color.shape:
                raise ValueError("color for sources must be a (N, 3) array "
                                 "(for rgb) or (N, 4) for rgba.")
            else:
                if (self.color.shape[1] is not 4):
                    self.color = self.color.T
                self.sColor = self.color

        # ======================== Check mask ========================
        # Check mask :
        if self.smask is not None:
            if (len(self.smask) != self.nSources) or not isinstance(
                                                    self.smask, np.ndarray):
                raise ValueError("The mask must be an array of bool with the "
                                 "same length as the number of electrodes")
            else:
                # Get the RGBA of mask color :
                self.sColor[self.smask, ...] = self.smaskcolor
        else:
            self.smask = np.zeros((self.nSources,), dtype=bool)

        # ======================== Check radius ========================
        # Check radius :
        if not isinstance(self.radiusmin, (int, float)):
            raise ValueError("s_radiusmin must be an integer or a float "
                             "number.")
        if not isinstance(self.radiusmax, (int, float)):
            raise ValueError("s_radiusmax must be an integer or a float "
                             "number.")
        if self.radiusmin >= self.radiusmax:
            raise ValueError("s_radiusmin must be > to s_radiusmax")

        # --------------------------------------------------------------------
        # Check data :
        if self.data is None:
            self.data = np.ones((self.nSources,), dtype=np.float32)
        if not np.ma.isMaskedArray(self.data):
            self.data = np.ma.masked_array(np.ravel(self.data),
                                           mask=self.smask.copy(),
                                           dtype=np.float32)
        if len(self.data) != self.nSources:
            raise ValueError("The length of data must be the same as the "
                             "number of electrodes")
        else:
            self.array2radius()

        # --------------------------------------------------------------------
        # Check text :
        if self.stext is not None:
            if len(self.stext) != len(self):
                raise ValueError("The length of text data must be the same "
                                 "as the number of electrodes")

    ##########################################################################
    # PLOTTING
    ##########################################################################
    def array2radius(self, factor=1.5):
        """Transform an array of data to source's radius.

        If data across sources is constant, the radiusmin will be used. If not,
        the source's radius will be modulated by the value of the data.
        """
        # Find radius either for constant / non-constant data :
        if np.unique(self.data.data).size == 1:  # Constant data
            self.sData = factor*self.radiusmin*np.ones((len(self.data.data),))
        else:                          # Non-constant values
            self.sData = normalize(self.data.data, tomin=factor*self.radiusmin,
                                   tomax=factor*self.radiusmax)

        # Rescale data :
        if self.scaling:
            self.sData /= self._rescale

    def plot(self):
        """Plot non-masked sources in the MNI brain.

        The sources are considered as a cloud of points to have only one
        more object on the final scene and make rendering / rotation faster
        compare to loop over single sources.
        """
        # Find only unmasked data :
        xyz, sData, sColor, _ = self._select_unmasked()

        # Render as cloud points :
        self.mesh = visu.Markers(name='Sources')
        self.mesh.set_data(xyz, edge_color=self.edgecolor, face_color=sColor,
                           size=sData, scaling=self.scaling,
                           edge_width=self.edgewidth, symbol=self.symbol)
        self.mesh.set_gl_state('translucent')

    def update(self):
        """Update sources without rendering.

        The only difference with the plot() method is that the update method
        doesn't recreate the cloud of point, it only re-set the data for
        non-masked sources. This is faster than re-create the source object.
        """
        # Find only unmasked data :
        xyz, sData, sColor, _ = self._select_unmasked()

        # Render as cloud points :
        if xyz.size:
            self.mesh.visible = True
            self.mesh.set_data(xyz, edge_color=self.edgecolor, size=sData,
                               face_color=sColor, scaling=self.scaling,
                               edge_width=self.edgewidth, symbol=self.symbol)
            # self.mesh.transform = self.transform
            self.mesh.update()
        else:
            self.mesh.visible = False

    ##########################################################################
    # MASK
    ##########################################################################
    def _select_unmasked(self):
        """Get some attributes of non-masked sources.

        Total sources: M, Non-masked sources: N

        Returns:
            xyz: array of shape (N, 3), float
                Coordinates of the non-masked sources

            data: array of shape (N,), float
                Data vector of the non-masked sources

            color: array of shape (N, 4), float
                RGBA color of the non-masked sources

            mask: array of shape (M,), bool
                The full source's mask
        """
        # Get unmasked data :
        mask = np.logical_not(self.data.mask)

        # Select unmasked sData and xyz :
        return self.xyz[mask, :], self.sData[mask], self.sColor[mask, :], mask

    def _reset_mask(self, reset_to=False):
        """Reset source's mask to a unique input.

        Kargs:
            reset_to: bool, optional, (def: False)
                The boolean value to use for reseting the mask.
        """
        self.data.mask = reset_to

    ##########################################################################
    # TEXT
    ##########################################################################
    def text_plot(self):
        """Plot some text for each source.

        The text is then translate to not cover the source. If no text is
        detected, a empty text object is created.
        """
        if self.stext is not None:
            # Create text object :
            self.stextmesh = visu.Text(text=self.stext, color=self.stextcolor,
                                       font_size=self.stextsize, pos=self.xyz,
                                       bold=True, name='SourcesText')

            # Set text texture :
            self.stextmesh.set_gl_state('translucent', depth_test=True)

            # Apply a transformation to text elements to not cover sources :
            self.stextmesh.transform = vist.STTransform(
                                                    translate=self.stextshift)
        else:
            self.stextmesh = visu.Text(name='NoneText')

    def text_update(self):
        """Update text elements of non-masked sources.

        The updated elements are:
            * The text
            * The text color
            * The font size
        """
        if self.stext is not None:
            # Get index of non-masked sources :
            idx = self._select_unmasked()[-1]

            # Set masked-sources text to '':
            text = np.array(self.stext)
            text[np.array(~idx, dtype=bool)] = ''

            # Update elements :
            self.stextmesh.text = text
            self.stextmesh.color = self.stextcolor
            self.stextmesh.font_size = self.stextsize
            self.stextmesh.update()
