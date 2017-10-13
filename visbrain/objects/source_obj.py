"""Base class for objects of type source."""
import numpy as np
from scipy.spatial.distance import cdist
from warnings import warn

from vispy import scene
from vispy.scene import visuals
import vispy.visuals.transforms as vist

from .visbrain_obj import VisbrainObject
from .roi_obj import RoiObj
from ..utils import tal2mni, color2vb, normalize, vispy_array


class SourceObj(VisbrainObject):
    """Create a source object.

    Parameters
    ----------
    name : string
        Name of the source object.
    xyz : array_like
        Array of positions of shape (n_sources, 2) or (n_sources, 3).
    data : array_like | None
        Array of weights of shape (n_sources,).
    color : array_like/string/tuple | 'black'
        Marker's color. Use a string (i.e 'green') to use the same color across
        markers or a list of colors of length n_sources to use different colors
        for markers.
    alpha : float | 1.
        Transparency level.
    symbol : string | 'disc'
        Symbol to use for sources. Allowed style strings are: disc, arrow,
        ring, clobber, square, diamond, vbar, hbar, cross, tailed_arrow, x,
        triangle_up, triangle_down, and star.
    radiusmin / radiusmax : float | 5.0/10.0
        Define the minimum and maximum source's possible radius. By default
        if all sources have the same value, the radius will be radiusmin.
    edge_color : string/list/array_like | 'black'
        Edge color of source's markers.
    edge_width : float | 0.
        Edge width source's markers.
    system : {'mni', 'tal'}
        Specify if the coodinates are in the MNI space ('mni') or Talairach
        ('tal').
    mask : array_like | None
        Array of boolean values to specify masked sources. For example, if data
        are p-values, mask could be non-significant sources.
    mask_color : array_like/tuple/string | 'red'
        Color to use for masked sources.
    text : list | None
        Text to attach to each source. For example, text could be the name of
        each source.
    text_size : float | 3.
        Text size attached to sources.
    text_color : array_like/string/tuple | 'black'
        Text color attached to sources.
    text_bold : bool | False
        Specify if the text attached to sources should be bold.
    text_shift : tuple | (0., 2., 0.)
        Text shifting along the (x, y, z) axis.
    visible : bool/array_like | True
        Specify which source's have to be displayed. If visible is True, all
        sources are displayed, False all sources are hiden. Alternatively, use
        an array of shape (n_sources,) to select which sources to display.
    parent : VisPy.parent | None
        Markers object parent.
    _z : float | 10.
        In case of (n_sources, 2) use _z to specify the elevation.
    """

    ###########################################################################
    ###########################################################################
    #                                BUILT IN
    ###########################################################################
    ###########################################################################

    def __init__(self, name, xyz, data=None, color='black', alpha=1.,
                 symbol='disc', radiusmin=5., radiusmax=10., edge_width=0.,
                 edge_color='black', system='mni', mask=None, mask_color='red',
                 text=None, text_size=3., text_color='black', text_bold=False,
                 text_shift=(0., 2., 0.), visible=True, parent=None, _z=-10.):
        """Init."""
        # Init Visbrain object base class :
        VisbrainObject.__init__(self, name, parent)
        # _______________________ CHECKING _______________________
        # XYZ :
        sh = xyz.shape
        assert sh[1] in [2, 3]
        self._n_sources = sh[0]
        pos = xyz if sh[1] == 3 else np.c_[xyz, np.full((len(self),), _z)]
        # Radius min and max :
        assert all([isinstance(k, (int, float)) for k in (
            radiusmin, radiusmax)])
        assert radiusmax >= radiusmin
        self._radiusmin, self._radiusmax = radiusmin, radiusmax
        # Data :
        if data is None:
            data = np.ones((len(self),))
        else:
            data = np.asarray(data).ravel()
            assert len(data) == len(self)
        self._data = vispy_array(data)
        # System :
        pos = pos if system == 'mni' else tal2mni(pos)
        self._xyz = vispy_array(pos)
        # Color :
        self._color, self._alpha = color, alpha
        # Mask :
        if mask is None:
            mask = [False] * len(self)
        self._mask = np.asarray(mask).ravel().astype(bool)
        assert len(self._mask) == len(self)
        self._mask_color = color2vb(mask_color)

        # _______________________ MARKERS _______________________
        self._sources = visuals.Markers(pos=self._xyz, name=name,
                                        edge_color=edge_color,
                                        edge_width=edge_width,
                                        parent=self._node)

        # _______________________ TEXT _______________________
        tvisible = text is None
        self._text = [''] * len(self) if tvisible else text
        assert len(self._text) == len(self)
        self._sources_text = visuals.Text(self._text, pos=self._xyz,
                                          bold=text_bold,
                                          color=color2vb(text_color),
                                          font_size=text_size,
                                          parent=self._node)
        self._sources_text.visible = not tvisible
        self._sources_text.transform = vist.STTransform(translate=text_shift)

        # _______________________ UPDATE _______________________
        # Radius / color :
        self.visible = visible
        self._update_radius()
        self._update_color()

    def __len__(self):
        """Get the number of sources."""
        return self._n_sources

    def __bool__(self):
        """Return if all source are visible."""
        return np.all(self._visible)

    def __iter__(self):
        """Loop over visible xyz coordinates.

        At each step, the coordinates are (1, 3) and not (3,).
        """
        xyz = self.xyz  # get only visible coordinates
        for k in range(xyz.shape[0]):
            yield xyz[[k], :]

    def __add__(self, value):
        """Add two SourceObj instances.

        This method return a SourceObj with xyz coodinates and the
        source's data but only for visible sources;
        """
        assert isinstance(value, SourceObj)
        name = self._name + ' + ' + value._name
        xyz = np.r_[self._xyz, value._xyz]
        data = np.r_[self._data, value._data]
        text = np.r_[self._text, value._text]
        visible = np.r_[self._visible, value.visible]
        return SourceObj(name, xyz, data=data, text=text, visible=visible)

    ###########################################################################
    ###########################################################################
    #                                UPDATE
    ###########################################################################
    ###########################################################################

    def update(self):
        """Update the source object."""
        self._sources.update()
        self._sources_text.update()

    def _update_radius(self):
        """Update marker's radius."""
        if np.unique(self._data).size == 1:
            radius = self._radiusmin * np.ones((len(self,)))
        else:
            radius = normalize(self._data, tomin=self._radiusmin,
                               tomax=self._radiusmax)
        self._sources._data['a_size'] = radius
        to_hide = self.hide
        # Marker size + egde width = 0 and text='' for hide sources :
        self._sources._data['a_size'][to_hide] = 0.
        self._sources._data['a_edgewidth'][to_hide] = 0.
        text = np.array(self._text.copy())
        text[to_hide] = ''
        self._sources_text.text = text
        self._sources.update()

    def _update_color(self):
        """Update marker's color."""
        # Get marker's background color :
        if isinstance(self._color, str):   # color='white'
            bg_color = color2vb(self._color, length=len(self))
        elif isinstance(self._color, list):  # color=['white', 'green']
            assert len(self._color) == len(self)
            bg_color = np.squeeze(np.array([color2vb(k) for k in self._color]))
        elif isinstance(self._color, np.ndarray):  # color = [[0, 0, 0], ...]
            csh = self._color.shape
            assert (csh[0] == len(self)) and (csh[1] >= 3)
            if self._color.shape[1] == 3:  # RGB
                self._color = np.c_[self._color, np.full(len(self),
                                                         self._alpha)]
            bg_color = self._color.copy()
        # Update masked marker's color :
        bg_color[self._mask, :] = self._mask_color
        self._sources._data['a_bg_color'] = bg_color

    def _get_camera(self):
        """Get the most adapted camera."""
        d_mean = self._xyz.mean(0)
        dist = np.sqrt(np.sum(d_mean ** 2))
        return scene.cameras.TurntableCamera(center=d_mean, scale_factor=dist)

    ###########################################################################
    ###########################################################################
    #                                  PHYSIO
    ###########################################################################
    ###########################################################################

    def analyse_sources(self, roi_obj='talairach', replace_bad=True,
                        bad_patterns=[-1, 'undefined', 'None'],
                        replace_with='Not found'):
        """Analyse sources using Region of interest (ROI).

        This method can be used to identify in which structure is located a
        source.

        Parameters
        ----------
        roi_obj : string/list | 'talairach'
            The ROI object to use. Use either 'talairach', 'brodmann' or 'aal'
            to use a predefined ROI template. Otherwise, use a RoiObj object or
            a list of RoiObj.
        replace_bad : bool | True
            Replace bad values (True) or not (False).
        bad_patterns : list | [-1, 'undefined', 'None']
            Bad patterns to replace if replace_bad is True.
        replace_with : string | 'Not found'
            Replace bad patterns with this string.

        Returns
        -------
        df : pandas.DataFrames
            A Pandas DataFrame or a list of DataFrames if roi_obj is a list.
        """
        # List of predefined ROI objects :
        proi = ['brodmann', 'aal', 'talairach']
        # Define the ROI object if needed :
        if isinstance(roi_obj, str):
            roi_obj = [roi_obj]
        # Convert predefined ROI into RoiObj objects :
        roi_obj = [RoiObj(k) for k in roi_obj if k in proi]
        if isinstance(roi_obj, (list, tuple)):
            test_r = all([k in proi or isinstance(k, RoiObj) for k in roi_obj])
            if not test_r:
                raise TypeError("roi_obj should either be 'brodmann', 'aal', "
                                "'talairach' or a list or RoiObj objects.")
        # Get all of the DataFrames :
        df = [k.localize_sources(self._xyz, self._text, replace_bad,
                                 bad_patterns, replace_with) for k in roi_obj]
        # Return the df if len == 1 :
        return df[0] if len(df) == 1 else df

    def color_sources(self, analysis, color_by, roi_to_color=None,
                      color_others='black', hide_others=False):
        """Color sources according to ROI analysis.

        Parameters
        ----------
        analysis : pandas.DataFrames
            ROI analysis runned using the analyse_sources method.
        color_by : string
            A column name of the analysis DataFrames. This columns is then used
            to identify the color to set to each source inside ROI.
        roi_to_color : dict | None
            Define custom colors to ROI. For example use {'BA4': 'red',
            'BA32': 'blue'} to define custom colors. If roi_to_color is None,
            random colors will be used instead.
        color_others : array_like/tuple/string | 'black'
            Specify how to color sources that are not found using the
            roi_to_color dictionary.
        hide_others : bool | False
            Show or hide sources that are not found using the
            roi_to_color dictionary.
        """
        # Group analysis :
        assert color_by in list(analysis.columns)
        gp = analysis.groupby(color_by).groups
        # Compute color :
        if roi_to_color is None:  # random color
            # Predefined colors and define unique color for each ROI :
            colors = np.zeros((len(self), 3), dtype=np.float32)
            u_col = np.random.uniform(.1, .8, (len(gp), 3)).astype(np.float32)
            # Assign color to the ROI :
            for k, index in enumerate(gp.values()):
                colors[list(index), :] = u_col[k, :]
        elif isinstance(roi_to_color, dict):  # user defined colors
            colors = color2vb(color_others, length=len(self))
            keep_visible = np.zeros(len(self), dtype=bool)
            for roi_name, roi_col in roi_to_color.items():
                if roi_name in list(gp.keys()):
                    colors[list(gp[roi_name]), :] = color2vb(roi_col)
                    keep_visible[list(gp[roi_name])] = True
                else:
                    warn(roi_name + " not found in the " + color_by + " column"
                         " of analysis.")
            if hide_others:
                self.visible = keep_visible
        else:
            raise TypeError("roi_to_color must either be None or a dictionary "
                            "like {'roi_name': 'red'}.")
        self.color = colors

    ###########################################################################
    ###########################################################################
    #                             PROJECTION
    ###########################################################################
    ###########################################################################

    @staticmethod
    def _get_eucl_mask(v, xyz, radius, contribute, xsign):
        # Compute euclidian distance and get sources under radius :
        eucl = cdist(v, xyz)
        eucl = eucl.astype(np.float32, copy=False)
        mask = eucl <= radius
        # Contribute :
        if not contribute:
            # Get vertices sign :
            vsign = np.sign(v[:, 0]).reshape(-1, 1)
            # Find where vsign and xsign are equals :
            isign = np.logical_and(vsign != xsign, xsign != 0)
            mask[isign] = False
        return eucl, mask

    def _check_projection(self, v, radius, contribute, not_masked=True):
        # =============== CHECKING ===============
        assert isinstance(v, np.ndarray)
        assert isinstance(radius, (int, float))
        assert isinstance(contribute, bool)
        if v.ndim == 2:  # index faced vertices
            v = v[:, np.newaxis, :]

        # =============== PRE-ALLOCATION ===============
        if not_masked:  # get only visible and not masked sources
            mask = self.visible_and_not_masked
        else:  # get only not visible and masked sources
            mask = ~self.visible_and_not_masked
        xyz, data = self._xyz[mask, :], self._data[mask]
        # Get sign of the x coordinate :
        xsign = np.sign(xyz[:, 0]).reshape(1, -1)

        return xyz, data, v, xsign

    def project_modulation(self, v, radius, contribute=False):
        """Project source's data onto vertices.

        Parameters
        ----------
        v : array_like
            The vertices of shape (nv, 3) or (nv, 3, 3) if index faced.
        radius : float
            The radius under which activity is projected on vertices.
        contribute: bool | False
            Specify if sources contribute on both hemisphere.

        Returns
        -------
        modulation : array_like
            The modulations of shape (nv, 3) or (nv, 3, 3) if index faced. This
            is a masked array where the mask refer to sources that are over the
            radius.
        """
        # Check inputs :
        xyz, data, v, xsign = self._check_projection(v, radius, contribute)
        index_faced = v.shape[1]
        # Modulation / proportion / (Min, Max) :
        modulation = np.ma.zeros((v.shape[0], index_faced), dtype=np.float32)
        prop = np.zeros_like(modulation.data)
        minmax = np.zeros((index_faced, 2), dtype=np.float32)

        # For each triangle :
        for k in range(index_faced):
            # =============== EUCLIDIAN DISTANCE ===============
            eucl, mask = self._get_eucl_mask(v[:, k, :], xyz, radius,
                                             contribute, xsign)
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

        return np.squeeze(modulation)

    def project_repartition(self, v, radius, contribute=False):
        """Project source's repartition onto vertices.

        Parameters
        ----------
        v : array_like
            The vertices of shape (nv, 3) or (nv, 3, 3) if index faced.
        radius : float
            The radius under which activity is projected on vertices.
        contribute: bool | False
            Specify if sources contribute on both hemisphere.

        Returns
        -------
        repartition: array_like
            The repartition of shape (nv, 3) or (nv, 3, 3) if index faced. This
            is a masked array where the mask refer to sources that are over the
            radius.
        """
        # Check inputs :
        xyz, _, v, xsign = self._check_projection(v, radius, contribute)
        index_faced = v.shape[1]
        # Corticale repartition :
        repartition = np.ma.zeros((v.shape[0], index_faced), dtype=np.int)

        # For each triangle :
        for k in range(index_faced):
            # =============== EUCLIDIAN DISTANCE ===============
            eucl, mask = self._get_eucl_mask(v[:, k, :], xyz, radius,
                                             contribute, xsign)

            # =============== REPARTITION ===============
            # Sum over sources dimension :
            sm = np.sum(mask, 1, dtype=np.int)
            smmask = np.invert(sm.astype(bool))
            repartition[:, k] = np.ma.masked_array(sm, mask=smmask)

        return np.squeeze(repartition)

    def get_masked_index(self, v, radius, contribute=False):
        """Get the index of masked source's under radius.

        Parameters
        ----------
        v : array_like
            The vertices of shape (nv, 3) or (nv, 3, 3) if index faced.
        radius : float
            The radius under which activity is projected on vertices.
        contribute: bool | False
            Specify if sources contribute on both hemisphere.

        Returns
        -------
        idx: array_like
            The repartition of shape (nv, 3) or (nv, 3, 3) if index faced.
        """
        # Check inputs and get masked xyz / data :
        xyz, data, v, xsign = self._check_projection(v, radius, contribute,
                                                     False)
        # Predefined masked euclidian distance :
        nv, index_faced = v.shape[0], v.shape[1]
        fmask = np.ones((v.shape[0], index_faced, len(data)), dtype=bool)

        # For each triangle :
        for k in range(index_faced):
            # =============== EUCLIDIAN DISTANCE ===============
            _, fmask[:, k, :] = self._get_eucl_mask(v[:, k, :], xyz, radius,
                                                    contribute, xsign)
        # Find where there's sources under radius and need to be masked :
        m = fmask.reshape(fmask.shape[0] * 3, fmask.shape[2])
        idx = np.dot(m, np.ones((len(data),), dtype=bool)).reshape(nv, 3)

        return np.squeeze(idx)

    def select_inside(self, v, select='inside'):
        """Select sources that are either inside or outside the mesh.

        Parameters
        ----------
        v : array_like
            The vertices of shape (nv, 3) or (nv, 3, 3) if index faced.
        select : {'inside', 'outside'}
            Use either 'inside' or 'outside'.
        """
        if v.ndim == 2:  # index faced vertices
            v = v[:, np.newaxis, :]
        xyz = self.xyz
        # Predifined inside :
        nv, index_faced = v.shape[0], v.shape[1]
        v = v.reshape(nv * index_faced, 3)
        inside = np.ones((xyz.shape[0],), dtype=bool)

        # Loop over sources :
        for i, k in enumerate(self):
            # Get the euclidian distance :
            eucl = cdist(v, k)
            # Get the closest vertex :
            eucl_argmin = eucl.argmin()
            # Get distance to zero :
            xyz_t0 = np.sqrt((k ** 2).sum())
            v_t0 = np.sqrt((v[eucl_argmin, :] ** 2).sum())
            inside[i] = xyz_t0 <= v_t0
        self.visible = inside if select == 'inside' else np.invert(inside)

    def fit_to_vertices(self, v):
        """Move sources to the closest vertex.

        Parameters
        ----------
        v : array_like
            The vertices of shape (nv, 3) or (nv, 3, 3) if index faced.
        """
        if v.ndim == 2:  # index faced vertices
            v = v[:, np.newaxis, :]
        xyz = self.xyz
        # Predifined inside :
        nv, index_faced = v.shape[0], v.shape[1]
        v = v.reshape(nv * index_faced, 3)
        new_pos = np.zeros_like(xyz)

        # Loop over visible and not-masked sources :
        for i, k in enumerate(self):
            # Get the euclidian distance :
            eucl = cdist(v, k)
            # Set new coordinate using the closest vertex :
            new_pos[i, :] = v[eucl.argmin(), :]
        # Finally update data sources and text :
        self._sources._data['a_position'] = new_pos
        self._sources_text.pos = new_pos
        self.update()

    ###########################################################################
    ###########################################################################
    #                             PROPERTIES
    ###########################################################################
    ###########################################################################

    # ----------- XYZ -----------
    @property
    def xyz(self):
        """Get the visible xyz value."""
        return self._xyz[self.visible_and_not_masked]

    # ----------- DATA -----------
    @property
    def data(self):
        """Get the data value."""
        return self._data[self.visible_and_not_masked]

    # ----------- TEXT -----------
    @property
    def text(self):
        """Get the text value."""
        return np.array(self._text)[self.visible_and_not_masked]

    # ----------- VISIBLE_AND_NOT_MASKED -----------
    @property
    def visible_and_not_masked(self):
        """Get the visible_and_not_masked value."""
        return np.logical_and(self._visible, ~self.mask)

    # ----------- RADIUSMIN -----------
    @property
    def radiusmin(self):
        """Get the radiusmin value."""
        return self._radiusmin

    @radiusmin.setter
    def radiusmin(self, value):
        """Set radiusmin value."""
        assert isinstance(value, (int, float))
        self._radiusmin = value
        self._update_radius()

    # ----------- RADIUSMAX -----------
    @property
    def radiusmax(self):
        """Get the radiusmax value."""
        return self._radiusmax

    @radiusmax.setter
    def radiusmax(self, value):
        """Set radiusmax value."""
        assert isinstance(value, (int, float))
        self._radiusmax = value
        self._update_radius()

    # ----------- SYMBOL -----------
    @property
    def symbol(self):
        """Get the symbol value."""
        return self._sources.symbol

    @symbol.setter
    def symbol(self, value):
        """Set symbol value."""
        self._sources.symbol = value
        self._sources.update()

    # ----------- EDGE_WIDTH -----------
    @property
    def edge_width(self):
        """Get the edge_width value."""
        return self._edge_width

    @edge_width.setter
    def edge_width(self, value):
        """Set edge_width value."""
        assert isinstance(value, (int, float))
        self._edge_width = value
        self._sources._data['a_edgewidth'] = value
        self._sources.update()

    # ----------- EDGE_COLOR -----------
    @property
    def edge_color(self):
        """Get the edge_color value."""
        return self._edge_color

    @edge_color.setter
    def edge_color(self, value):
        """Set edge_color value."""
        color = color2vb(value)
        self._sources._data['a_fg_color'] = color
        self._edge_color = color
        self._sources.update()

    # ----------- ALPHA -----------
    @property
    def alpha(self):
        """Get the alpha value."""
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        """Set alpha value."""
        assert isinstance(value, (int, float))
        assert 0 <= value <= 1
        self._alpha = value
        self._sources._data['a_fg_color'][:, -1] = value
        self._sources._data['a_bg_color'][:, -1] = value
        self._sources.update()

    # ----------- COLOR -----------
    @property
    def color(self):
        """Get the color value."""
        return self._color

    @color.setter
    def color(self, value):
        """Set color value."""
        self._color = value
        self._update_color()

    # ----------- MASK -----------
    @property
    def mask(self):
        """Get the mask value."""
        return self._mask

    @mask.setter
    def mask(self, value):
        """Set mask value."""
        assert len(value) == len(self)
        self._mask = value
        self._update_color()

    # ----------- MASKCOLOR -----------
    @property
    def mask_color(self):
        """Get the mask_color value."""
        return self._mask_color

    @mask_color.setter
    def mask_color(self, value):
        """Set mask_color value."""
        self._mask_color = color2vb(value)
        self._update_color()

    # ----------- VISIBLE -----------
    @property
    def visible(self):
        """Get the visible value."""
        return self._visible

    @visible.setter
    def visible(self, value):
        """Set visible value."""
        if isinstance(value, bool):
            self._visible = np.full((len(self),), value)
        else:
            self._visible = np.asarray(value).ravel().astype(bool)
        assert len(self._visible) == len(self)
        self._update_radius()

    # ----------- HIDE -----------
    @property
    def hide(self):
        """Get the hide value."""
        return np.invert(self._visible)

    @hide.setter
    def hide(self, value):
        """Set hide value."""
        self._hide = value

    # ----------- TEXT_SIZE -----------
    @property
    def text_size(self):
        """Get the text_size value."""
        return self._text_size

    @text_size.setter
    def text_size(self, value):
        """Set text_size value."""
        assert isinstance(value, (int, float))
        self._text_size = value
        self._sources_text.font_size = value
        self._sources_text.update()

    # ----------- TEXT_COLOR -----------
    @property
    def text_color(self):
        """Get the text_color value."""
        return self._text_color

    @text_color.setter
    def text_color(self, value):
        """Set text_color value."""
        color = color2vb(value)
        self._sources_text.color = color
        self._text_color = color
        self._sources_text.update()

    # ----------- TEXT_SHIFT -----------
    @property
    def text_shift(self):
        """Get the text_shift value."""
        return self._text_shift

    @text_shift.setter
    def text_shift(self, value):
        """Set text_shift value."""
        assert len(value) == 3
        self._sources_text.transform.translate = value
        self._text_shift = value
        self._sources_text.update()

# proj_doc = """v : array_like
#             The vertices of shape (nv, 3) or (nv, 3, 3) if index faced.
#         radius : float
#             The radius under which activity is projected on vertices.
#         contribute: bool | False
#             Specify if sources contribute on both hemisphere."""
# for k in ['project_modulation', 'project_repartition', 'get_masked_index']:
#     st = 'SourceObj.%s.__doc__' % k
#     exec('%s = %s.format(proj_doc)' % (st, st))
