"""Base class for sources and text sources managment.

Sources are small deep / surface points. It can materialize intracranial
electrodes or EEG / MEG captor. Each source can have an associated activity
that can be then projected on the surface.

This class is responsible of creating and add some utility functions for
sources objects.
"""

import numpy as np
from scipy.spatial.distance import cdist

import vispy.scene.visuals as visu
import vispy.visuals.transforms as vist

from ...utils import color2vb, normalize, tal2mni
from ...visuals import CbarArgs

__all__ = ('SourcesBase')


class SourcesBase(CbarArgs):
    """Initialize the source object and to add some necessary functions.

    This class can be used for like plotting, loading... Each source's input
    start with 's_'. Other arguments (**kwargs) are ignored. This class is also
    responsible for associated text to each source.
    """

    def __init__(self, s_xyz=None, s_data=None, s_color='#ab4652',
                 s_opacity=1.0, s_radiusmin=5.0, s_radiusmax=10.0,
                 s_edgecolor=None, s_edgewidth=0.6, s_scaling=False,
                 s_text=None, s_symbol='disc', s_textcolor='white',
                 s_textsize=3, s_textshift=(0, 2, 0), s_mask=None,
                 s_maskcolor='gray', s_cmap='inferno', s_clim=(0., 1.),
                 s_vmin=None, s_vmax=None, s_under=None, s_over=None,
                 s_projecton='surface', s_system='mni', **kwargs):
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
        self.system = s_system
        self._defcolor = 'slateblue'
        self._rescale = 3.0

        # Plot :
        if self.xyz is not None:
            self.prepare2plot()
            self.plot()
            self.text_plot()
        else:
            self.mesh = visu.Markers(name='NoneSources')
            self.stextmesh = visu.Text(name='NoneText')

        # Vmin/Vmax only active if not None and in [clim[0], clim[1]] :
        isvmin = (s_vmin is not None) and (
            s_clim[0] < s_vmin < s_clim[1])
        isvmax = (s_vmax is not None) and (
            s_clim[0] < s_vmax < s_clim[1])
        # Initialize colorbar elements :
        CbarArgs.__init__(self, s_cmap, s_clim, isvmin, s_vmin,
                          isvmax, s_vmax, s_under, s_over)

    def __len__(self):
        """Get the length of non-masked sources."""
        return len(np.where(np.logical_not(self.data.mask))[0])

    def __iter__(self):
        """Iterate over sources coordinates."""
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
        # Check coordinate system :
        if self.system not in ['mni', 'tal']:
            raise ValueError("The s_system must either be 'mni' or 'tal'.")
        elif self.system is 'tal':
            self.xyz = tal2mni(self.xyz)

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
            if self.color.shape == (1, 3) or self.color.shape == (1, 4):
                self.sColor = np.tile(self.color, (self.nSources, 1))
            elif self.nSources in self.color.shape:
                if (self.color.shape[1] is not 4):
                    self.color = self.color.T
                self.sColor = self.color
            else:
                raise ValueError("color for sources must be a (N, 3) array "
                                 "(for rgb) or (N, 4) for rgba.")

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
                                           mask=self.smask.copy())
        if len(self.data) != self.nSources:
            raise ValueError("The length of data must be the same as the "
                             "number of electrodes")
        else:
            self.array2radius()

        # --------------------------------------------------------------------
        # Check text :
        if self.stext is not None:
            if len(self.stext) != len(self.data):
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
        # xyz, sData, sColor, _ = self._select_unmasked()
        xyz, sData, sColor = self.xyz, self.sData, self.sColor

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
        # xyz, sData, sColor = self.xyz, self.sData, self.sColor

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
    def display(self, select='all'):
        """Choose which sources to display.

        Args:
            select: string
                Use either 'all', 'none', 'left' or 'right'.
        """
        if select == 'all':
            idx = slice(0)
        elif select == 'none':
            idx = slice(None)
        if select == 'left':
            idx = self.xyz[:, 0] >= 0
        elif select == 'right':
            idx = self.xyz[:, 0] <= 0
        # Hide souces :
        self.data.mask = False
        self.data.mask[idx] = True
        # Update data sources and text :
        self.update()
        self.text_update()

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
    # PROJECTIONS
    ##########################################################################
    def _modulation(self, v, radius, contribute=False):
        """Get data modulated by the euclidian distance.

        The vertices are indexed by face which means it's a (N, 3, 3).
        Depending on the number of sources, using broadcasting rules can
        be memory consuming. For that reason, we split computation for each
        face, using an ugly loop.

        Args:
            v: np.ndarray, float32
                The index faced vertices of shape (nv, 3, 3)

            radius: float
                The radius under which activity is projected on vertices.

        Kargs:
            contribute: bool, optional, (def: False)
                Specify if sources contribute on both hemisphere.

        Return:
            modulation: masked np.ndarray, float32
                The index faced modulations of shape (N, 3). This is a masked
                array where the mask refer to sources that are over the radius.
        """
        # =============== PRE-ALLOCATION ===============
        # Compute on non-masked sources :
        masked = ~self.data.mask
        xyz = self.xyz[masked]
        data = self.data.data[masked].astype(np.float32)
        # Get sign of the x coordinate :
        xsign = np.sign(xyz[:, 0]).reshape(1, -1)
        # Modulation / proportion / (Min, Max) :
        modulation = np.ma.zeros((v.shape[0], v.shape[1]), dtype=np.float32)
        prop = np.zeros_like(modulation.data)
        minmax = np.zeros((3, 2), dtype=np.float32)

        # For each triangle :
        for k in range(3):
            # =============== EUCLIDIAN DISTANCE ===============
            # Compute euclidian distance and get sources under radius :
            eucl = cdist(v[:, k, :], xyz)
            eucl = eucl.astype(np.float32, copy=False)
            mask = eucl <= radius
            # Contribute :
            if not contribute:
                # Get vertices signn :
                vsign = np.sign(v[:, k, 0]).reshape(-1, 1)
                # Find where vsign and xsign are equals :
                isign = np.logical_and(vsign != xsign, xsign != 0)
                mask[isign] = False
            # Invert euclidian distance for modulation and mask it :
            np.multiply(eucl, -1. / eucl.max(), out=eucl)
            np.add(eucl, 1., out=eucl)
            eucl = np.ma.masked_array(eucl, mask=np.invert(mask),
                                      dtype=np.float32)

            # =============== MODULATION ===============
            # Modulate data by distance (only for sources under radius) :
            modulation[:, k] = np.ma.dot(eucl, data, strict=False)

            # =============== PROPORTIONS ===============
            np.sum(mask, axis=1, dtype=np.float32, out=prop[:, k])
            nnz = np.nonzero(mask.sum(0))
            minmax[k, :] = np.array([data[nnz].min(), data[nnz].max()])

        # Divide modulations by the number of contributing sources :
        prop[prop == 0.] = 1.
        np.divide(modulation, prop, out=modulation)
        # Normalize inplace modulations between under radius data :
        normalize(modulation, minmax.min(), minmax.max())

        return modulation

    def _repartition(self, v, radius, contribute=False):
        """Get data repartition.

        The vertices are indexed by face which means it's a (N, 3, 3).
        Depending on the number of sources, using broadcasting rules can
        be memory consuming. For that reason, we split computation for each
        face, using an ugly loop.

        Args:
            v: np.ndarray, float32
                The index faced vertices of shape (nv, 3, 3)

            radius: float
                The radius under which activity is projected on vertices.

        Kargs:
            contribute: bool, optional, (def: False)
                Specify if sources contribute on both hemisphere.

        Return:
            repartition: masked np.ndarray, float32
                The index faced repartition of shape (N, 3). This is a masked
                array where the mask refer to sources that are over the radius.
        """
        # =============== PRE-ALLOCATION ===============
        # Compute on non-masked sources :
        xyz = self.xyz[~self.data.mask]
        # Get sign of the x coordinate :
        xsign = np.sign(xyz[:, 0]).reshape(1, -1)
        # Corticale repartition :
        repartition = np.ma.zeros((v.shape[0], v.shape[1]), dtype=np.int)

        # For each triangle :
        for k in range(3):
            # =============== EUCLIDIAN DISTANCE ===============
            eucl = cdist(v[:, k, :], xyz).astype(np.float32)
            mask = eucl <= radius
            # Contribute :
            if not contribute:
                # Get vertices signn :
                vsign = np.sign(v[:, k, 0]).reshape(-1, 1)
                # Find where vsign and xsign are equals :
                isign = np.logical_and(vsign != xsign, xsign != 0)
                mask[isign] = False

            # =============== REPARTITION ===============
            # Sum over sources dimension :
            sm = np.sum(mask, 1, dtype=np.int)
            smmask = np.invert(sm.astype(bool))
            repartition[:, k] = np.ma.masked_array(sm, mask=smmask)

        return repartition

    def _MaskedEucl(self, v, radius, contribute=False):
        """Get the index of masked source's under radius.

        Args:
            v: np.ndarray, float32
                The index faced vertices of shape (nv, 3, 3)

            radius: float
                The radius under which activity is projected on vertices.

        Kargs:
            contribute: bool, optional, (def: False)
                Specify if sources contribute on both hemisphere.

        Return:
            repartition: masked np.ndarray, float32
                The index faced repartition of shape (N, 3). This is a masked
                array where the mask refer to sources that are over the radius.

        """
        # Select only masked xyz / data :
        masked = self.data.mask
        xyz, data = self.xyz[masked, :], self.data.data[masked]
        # Get sign of the x coordinate :
        xsign = np.sign(xyz[:, 0]).reshape(1, -1)
        # Predefined masked euclidian distance :
        nv = v.shape[0]
        fmask = np.ones((v.shape[0], 3, len(data)), dtype=bool)

        # For each triangle :
        for k in range(3):
            # =============== EUCLIDIAN DISTANCE ===============
            eucl = cdist(v[:, k, :], xyz).astype(np.float32)
            fmask[:, k, :] = eucl <= radius
            # Contribute :
            if not contribute:
                # Get vertices signn :
                vsign = np.sign(v[:, k, 0]).reshape(-1, 1)
                # Find where vsign and xsign are equals :
                isign = np.logical_and(vsign != xsign, xsign != 0)
                fmask[:, k, :][isign] = False
        # Find where there's sources under radius and need to be masked :
        m = fmask.reshape(fmask.shape[0] * 3, fmask.shape[2])
        idx = np.dot(m, np.ones((len(data),), dtype=bool)).reshape(nv, 3)

        return idx

    def _isInside(self, v, select, progress):
        """Select sources that are either inside or outside the mesh.

        This method directly hide sources.

        Args:
            v: np.ndarray, float32
                The index faced vertices of shape (nv, 3, 3)

            select: string
                Use either 'inside' or 'outside'.

            progress: pyqt progress bar
                The progress bar.
        """
        # Compute on non-masked sources :
        xyz = self.xyz
        N = xyz.shape[0]
        inside = np.ones((xyz.shape[0],), dtype=bool)
        v = v.reshape(v.shape[0] * 3, 3)

        # Loop over sources :
        progress.show()
        for k in range(N):
            # Get the euclidian distance :
            eucl = cdist(v, xyz[[k], :])
            # Get the closest vertex :
            eucl_argmin = eucl.argmin()
            # Get distance to zero :
            xyz_t0 = np.sqrt((xyz[k, :] ** 2).sum())
            v_t0 = np.sqrt((v[eucl_argmin, :] ** 2).sum())
            inside[k] = xyz_t0 <= v_t0
            progress.setValue(100 * k / N)
        self.data.mask = False
        self.data.mask = inside if select != 'inside' else np.invert(inside)
        # Finally update data sources and text :
        self.update()
        self.text_update()
        progress.hide()

    def _fit(self, v, progress):
        """Move sources to the closest vertex.

        This method directly hide sources.

        Args:
            v: np.ndarray, float32
                The index faced vertices of shape (nv, 3, 3)

            progress: pyqt progress bar
                The progress bar.
        """
        # Compute on non-masked sources :
        xyz = self.xyz
        N = xyz.shape[0]
        v = v.reshape(v.shape[0] * 3, 3)

        # Loop over sources :
        progress.show()
        for k in range(N):
            # Get the euclidian distance :
            eucl = cdist(v, xyz[[k], :])
            # Get the closest vertex :
            eucl_argmin = eucl.argmin()
            # Set new coordinate :
            self.xyz[k, :] = v[eucl_argmin, :]
        # Finally update data sources and text :
        self.update()
        self.text_update()
        progress.hide()

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
            # idx = self._select_unmasked()[-1]

            # Set masked-sources text to '':
            text = np.array(self.stext)
            # text[np.array(~idx, dtype=bool)] = ''

            # Update elements :
            self.stextmesh.text = text
            self.stextmesh.color = self.stextcolor
            self.stextmesh.font_size = self.stextsize
            self.stextmesh.update()

    # ----------- NAME -----------
    @property
    def name(self):
        """Get the name value."""
        return self.mesh.name
