"""Base class for objects of type connectivity."""
import logging

import numpy as np
from collections import Counter

from vispy import scene
from vispy.scene import visuals

from .visbrain_obj import VisbrainObject, CombineObjects
from .source_obj import SourceObj
from ..utils import (array2colormap, color2vb, wrap_properties,
                     vector_to_opacity)


logger = logging.getLogger('visbrain')


class ConnectObj(VisbrainObject):
    """Create a connectivity object.

    Parameters
    ----------
    name : string
        The name of the connectivity object.
    nodes : array_like
        Array of nodes coordinates of shape (n_nodes, 3).
    edges : array_like | None
        Array of ponderations for edges of shape (n_nodes, n_nodes).
    select : array_like | None
        Array to select edges to display. This should be an array of boolean
        values of shape (n_nodes, n_nodes).
    line_width : float | 3.
        Connectivity line width.
    color_by : {'strength', 'count', 'causal'}
        Coloring method:

            * 'strength' : color edges according to their connection strength
              define by the `edges` input. Only the upper triangle of the
              connectivity array is considered.
            * 'count' : color edges according to the number of connections per
              node. Only the upper triangle of the connectivity array is
              considered.
            * 'causal' : color edges according to the connectivity strength but
              this time, the upper and lower triangles of the connectivity
              array in `edges` are considered.
    custom_colors : dict | None
        Use a dictionary to colorize edges. For example, {1.2: 'red',
        2.8: 'green', None: 'black'} turn connections that have a 1.2 and 2.8
        strength into red and green. All others connections are set to black.
    alpha : float | 1.
        Transparency level (if dynamic is None).
    antialias : bool | False
        Use smoothed lines.
    dynamic : tuple | None
        Control the dynamic opacity. For example, if dynamic=(0, 1),
        strong connections will be more opaque than weaker connections.
    dynamic_order : int | 1
        If 1, the dynamic transparency is linearly modulated by the
        connectivity. If 2, the transparency follow a x**2 curve etc.
    dynamic_orientation : str | 'ascending'
        Define the transparency behavior :

            * 'ascending' : from translucent to opaque
            * 'center' : from opaque to translucent and finish by opaque
            * 'descending' ; from opaque to translucent
    cmap : string | 'viridis'
        Colormap to use if custom_colors is None.
    vmin : float | None
        Lower threshold of the colormap if custom_colors is None.
    under : string | None
        Color to use for values under vmin if custom_colors is None.
    vmin : float | None
        Higher threshold of the colormap if custom_colors is None.
    over : string | None
        Color to use for values over vmax if custom_colors is None.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Line object parent.
    verbose : string
        Verbosity level.
    _z : float | 10.
        In case of (n_sources, 2) use _z to specify the elevation.
    kw : dict | {}
        Optional arguments are used to control the colorbar
        (See :class:`ColorbarObj`).

    Notes
    -----
    List of supported shortcuts :

        * **s** : save the figure
        * **<delete>** : reset camera


    Examples
    --------
    >>> import numpy as np
    >>> from visbrain.objects import ConnectObj
    >>> n_nodes = 100
    >>> nodes = np.random.rand(n_nodes, 3)
    >>> edges = np.random.uniform(low=-10., high=10., size=(n_nodes, n_nodes))
    >>> select = np.logical_and(edges >= 0, edges <= 1.)
    >>> c = ConnectObj('Connect', nodes, edges, select=select, cmap='inferno',
    >>>                antialias=True)
    >>> c.preview(axis=True)
    """

    ###########################################################################
    ###########################################################################
    #                                BUILT IN
    ###########################################################################
    ###########################################################################

    def __init__(self, name, nodes, edges, select=None, line_width=3.,
                 color_by='strength', custom_colors=None, alpha=1.,
                 antialias=False, dynamic=None, dynamic_order=1,
                 dynamic_orientation='ascending', cmap='viridis', clim=None,
                 vmin=None, vmax=None, under='gray', over='red',
                 transform=None, parent=None, verbose=None, _z=-10., **kw):
        """Init."""
        VisbrainObject.__init__(self, name, parent, transform, verbose, **kw)
        self._update_cbar_args(cmap, clim, vmin, vmax, under, over)

        # _______________________ CHECKING _______________________
        # Nodes :
        assert isinstance(nodes, np.ndarray) and nodes.ndim == 2
        sh = nodes.shape
        self._n_nodes = sh[0]
        assert sh[1] >= 2
        pos = nodes if sh[1] == 3 else np.c_[nodes, np.full((len(self),), _z)]
        self._pos = pos.astype(np.float32)
        logger.info("    %i nodes detected" % self._pos.shape[0])
        # Edges :
        assert edges.shape == (len(self), len(self))
        if not np.ma.isMA(edges):
            mask = np.zeros(edges.shape, dtype=bool)
            edges = np.ma.masked_array(edges, mask=mask)
        # Select :
        if isinstance(select, np.ndarray):
            assert select.shape == edges.shape and select.dtype == bool
            edges.mask = np.invert(select)
        if color_by is not 'causal':
            edges.mask[np.tril_indices(len(self), 0)] = True
        edges.mask[np.diag_indices(len(self))] = True
        self._edges = edges
        # Colorby :
        assert color_by in ['strength', 'count', 'causal']
        self._color_by = color_by
        # Dynamic :
        if dynamic is not None:
            assert len(dynamic) == 2
        self._dynamic = dynamic
        assert isinstance(dynamic_order, int) and dynamic_order > 0
        self._dyn_order = dynamic_order
        self._dyn_orient = dynamic_orientation
        # Custom color :
        if custom_colors is not None:
            assert isinstance(custom_colors, dict)
        self._custom_colors = custom_colors
        # Alpha :
        assert 0. <= alpha <= 1.
        self._alpha = alpha

        # _______________________ LINE _______________________
        self._connect = visuals.Line(name='ConnectObjLine', width=line_width,
                                     antialias=antialias, parent=self._node,
                                     connect='segments')
        self._connect.set_gl_state('translucent', depth_test=False,
                                   cull_face=False)
        self._build_line()

    def __len__(self):
        """Get the number of nodes."""
        return self._n_nodes

    def update(self):
        """Update the line."""
        self._connect.update()

    def _build_line(self):
        """Build the connectivity line."""
        pos, edges = self._pos, self._edges
        # Color either edges or nodes :
        logger.info("    %s coloring method for connectivity" % self._color_by)
        # Switch between coloring method :
        if self._color_by in ['strength', 'count']:
            # Build line position
            nnz_x, nnz_y = np.where(~edges.mask)
            indices = np.c_[nnz_x, nnz_y].flatten()
            line_pos = pos[indices, :]
            if self._color_by == 'strength':
                nnz_values = edges.compressed()
                values = np.c_[nnz_values, nnz_values].flatten()
            elif self._color_by == 'count':
                node_count = Counter(np.ravel([nnz_x, nnz_y]))
                values = np.array([node_count[k] for k in indices])
        elif self._color_by == 'causal':
            idx = np.array(np.where(~edges.mask)).T
            # If the array is not symetric, the line needs to be drawn between
            # points. If it's symetric, line should stop a the middle point.
            # Here, we get the maske value of the symetric and use it to
            # ponderate middle point calculation :
            pond = (~np.array(edges.mask))[idx[:, 1], idx[:, 0]]
            pond = pond.astype(float).reshape(-1, 1)
            div = pond + 1.
            # Build line pos :
            line_pos = np.zeros((2 * idx.shape[0], 3), dtype=float)
            line_pos[0::2, :] = pos[idx[:, 0], :]
            line_pos[1::2, :] = (pos[idx[:, 1]] + pond * pos[idx[:, 0]]) / div
            # Build values :
            values = np.full((line_pos.shape[0],), edges.min(), dtype=float)
            values[1::2] = edges.compressed()
        logger.info("    %i connectivity links displayed" % line_pos.shape[0])
        self._minmax = (values.min(), values.max())
        if self._clim is None:
            self._clim = self._minmax

        # Get the color according to values :
        if isinstance(self._custom_colors, dict):  # custom color
            if None in list(self._custom_colors.keys()):  # {None : 'color'}
                color = color2vb(self._custom_colors[None], length=len(values))
            else:  # black by default
                color = np.zeros((len(values), 4), dtype=np.float32)
            for val, col in self._custom_colors.items():
                color[values == val, :] = color2vb(col)
        else:
            color = array2colormap(values, **self.to_kwargs())
        color[:, -1] = self._alpha

        # Dynamic color :
        if self._dynamic is not None:
            color[:, 3] = vector_to_opacity(values, clim=self._clim,
                                            dyn=self._dynamic,
                                            order=self._dyn_order,
                                            orientation=self._dyn_orient)

        # Send data to the connectivity object :
        self._connect.set_data(pos=line_pos, color=color)

    def get_nb_connections_per_node(self, sort='index', order='ascending'):
        """Get the number of connections per node.

        Parameters
        ----------
        sort : {'index', 'count'}
            Sort either by node index ('index') or according to the number of
            connections per node ('count').
        order : {'ascending', 'descending'}
            Get the number of connections per node
        """
        return self._get_nb_connect(self._edges.mask, sort, order)

    def analyse_connections(self, roi_obj='talairach', group_by=None,
                            get_centroids=False, replace_bad=True,
                            bad_patterns=[-1, 'undefined', 'None'],
                            distance=None, replace_with='Not found',
                            keep_only=None):
        """Analyse connections.

        Parameters
        ----------
        roi_obj : string/list | 'talairach'
            The ROI object to use. Use either 'talairach', 'brodmann' or 'aal'
            to use a predefined ROI template. Otherwise, use a RoiObj object or
            a list of RoiObj.
        group_by : str | None
            Name of the column inside the dataframe for gouping connectivity
            results.
        replace_bad : bool | True
            Replace bad values (True) or not (False).
        bad_patterns : list | [-1, 'undefined', 'None']
            Bad patterns to replace if replace_bad is True.
        replace_with : string | 'Not found'
            Replace bad patterns with this string.
        keep_only : list | None
            List of string patterns to keep only sources that match.

        Returns
        -------
        df : pandas.DataFrames
            A Pandas DataFrame or a list of DataFrames if roi_obj is a list.
        """
        # Get anatomical info of sources :
        s_obj = SourceObj('analyse', self._pos)
        df = s_obj.analyse_sources(roi_obj=roi_obj, replace_bad=replace_bad,
                                   bad_patterns=bad_patterns,
                                   distance=distance,
                                   replace_with=replace_with,
                                   keep_only=keep_only)
        # If no column, return the full dataframe :
        if group_by is None:
            return df
        # Group DataFrame column :
        grp = df.groupby(group_by).groups
        labels, index = list(grp.keys()), list(grp.values())
        # Prepare the new connectivity array :
        n_labels = len(labels)
        x_r = np.zeros((n_labels, n_labels), dtype=float)
        mask_r = np.ones((n_labels, n_labels), dtype=bool)
        # Loop over the upper triangle :
        row, col = np.triu_indices(n_labels)
        data, mask = self._edges.data, self._edges.mask
        for r, c in zip(row, col):
            m = tuple(np.meshgrid(index[r], index[c]))
            x_r[r, c], mask_r[r, c] = data[m].mean(), mask[m].all()
        # Define a ROI dataframe :
        import pandas as pd
        columns = [group_by, "Mean connectivity strength inside ROI",
                   "Number of connections per node"]
        df_roi = pd.DataFrame({}, columns=columns)
        df_roi[group_by] = labels
        df_roi[columns[1]] = np.diag(x_r)
        df_roi[columns[2]] = [len(k) for k in index]
        # Get (x, y, z) ROI centroids :
        if get_centroids:
            # Define the RoiObj :
            from .roi_obj import RoiObj
            if isinstance(roi_obj, str):
                r_obj = RoiObj(roi_obj)
            assert isinstance(r_obj, RoiObj)
            # Search where is the label :
            idx, roi_labels, rm_rows = [], [], []
            for k, l in enumerate(labels):
                _idx = r_obj.where_is(l, exact=True)
                if not len(_idx):
                    rm_rows += [k]
                else:
                    idx += [_idx[0]]
                    roi_labels += [l]
            xyz = r_obj.get_centroids(idx)
            x_r = np.delete(x_r, rm_rows, axis=0)
            x_r = np.delete(x_r, rm_rows, axis=1)
            mask_r = np.delete(mask_r, rm_rows, axis=0)
            mask_r = np.delete(mask_r, rm_rows, axis=1)
            df_roi.drop(rm_rows, inplace=True)
            df_roi.index = pd.RangeIndex(len(df_roi.index))
            df_roi['X'] = xyz[:, 0]
            df_roi['Y'] = xyz[:, 1]
            df_roi['Z'] = xyz[:, 2]
        x_r = np.ma.masked_array(x_r, mask=mask_r)
        return x_r, labels, df_roi

    @staticmethod
    def _get_nb_connect(mask, sort, order):
        """Sub-function to get the number of connections per node."""
        assert sort in ['index', 'count'], \
            ("`sort` should either be 'index' or 'count'")
        assert order in ['ascending', 'descending'], \
            ("`order` should either be 'ascending' or 'descending'")
        logger.info("    Get the number of connections per node")
        n_nodes = mask.shape[0]
        # Get the number of connections per nodes :
        nnz_x, nnz_y = np.where(~mask)
        dict_ord = dict(Counter(np.ravel([nnz_x, nnz_y])))
        # Full number of connections :
        nb_connect = np.zeros((n_nodes, 2), dtype=int)
        nb_connect[:, 0] = np.arange(n_nodes)
        nb_connect[list(dict_ord.keys()), 1] = list(dict_ord.values())
        # Sort according to node index or number of connections per node :
        idx = 0 if sort is 'index' else 1
        args = np.argsort(nb_connect[:, idx])
        # Ascending or descending sorting :
        if order == 'descending':
            args = np.flip(args)
        return nb_connect[args, :]

    def _get_camera(self):
        """Get the most adapted camera."""
        d_mean = self._pos.mean(0)
        dist = np.sqrt(np.sum(d_mean ** 2))
        cam = scene.cameras.TurntableCamera(center=d_mean, scale_factor=dist)
        self.camera = cam
        return cam

    ###########################################################################
    ###########################################################################
    #                             PROPERTIES
    ###########################################################################
    ###########################################################################

    # ----------- LINE_WIDTH -----------
    @property
    def line_width(self):
        """Get the line_width value."""
        return self._connect.width

    @line_width.setter
    @wrap_properties
    def line_width(self, value):
        """Set line_width value."""
        assert isinstance(value, (int, float))
        self._connect._width = value
        self.update()

    # ----------- COLOR_BY -----------
    @property
    def color_by(self):
        """Get the color_by value."""
        return self._color_by

    @color_by.setter
    @wrap_properties
    def color_by(self, value):
        """Set color_by value."""
        assert value in ['strength', 'count', 'causal']
        self._color_by = value
        self._build_line()

    # ----------- DYNAMIC -----------
    @property
    def dynamic(self):
        """Get the dynamic value."""
        return self._dynamic

    @dynamic.setter
    @wrap_properties
    def dynamic(self, value):
        """Set dynamic value."""
        assert value is None or len(value) == 2
        self._dynamic = value
        self._build_line()

    # ----------- ALPHA -----------
    @property
    def alpha(self):
        """Get the alpha value."""
        return self._alpha

    @alpha.setter
    @wrap_properties
    def alpha(self, value):
        """Set alpha value."""
        assert 0. <= value <= 1.
        self._connect.color[:, -1] = value
        self._alpha = value
        self.update()


class CombineConnect(CombineObjects):
    """Combine connectivity objects.

    Parameters
    ----------
    cobjs : ConnectObj/list | None
        List of source objects.
    select : string | None
        The name of the connectivity object to select.
    parent : VisPy.parent | None
        Markers object parent.
    """

    def __init__(self, cobjs=None, select=None, parent=None):
        """Init."""
        CombineObjects.__init__(self, ConnectObj, cobjs, select, parent)
