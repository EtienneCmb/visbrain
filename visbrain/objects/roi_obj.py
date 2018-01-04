"""Base class for objects of type ROI."""
import os
import logging
from functools import wraps

import numpy as np
from scipy.spatial.distance import cdist

from vispy import scene
from vispy.geometry.isosurface import isosurface

from .volume_obj import _Volume, _CombineVolume
from ._projection import _project_sources_data
from ..io import is_pandas_installed
from ..utils import (mni2tal, smooth_3d, color2vb)
from ..visuals import BrainMesh

logger = logging.getLogger('visbrain')


def wrap_setter_properties(fn):
    """Set properties if not None and if mesh is defined."""
    @wraps(fn)
    def wrapper(self, value):
        if (value is not None) and self:
            fn(self, value)
    return wrapper


def wrap_getter_properties(fn):
    """Get properties if mesh is defined."""
    @wraps(fn)
    def wrapper(self):
        if self:
            return fn(self)
        else:
            raise ValueError("No mesh defined. Use the method `select_roi` "
                             "before")
    return wrapper


class RoiObj(_Volume):
    """Create a Region Of Interest (ROI) object.

    Parameters
    ----------
    name : string
        Name of the ROI object. If name is 'brodmann', 'aal' or 'talairach' a
        predefined ROI object is used and vol, index and label are ignored.
    vol : array_like | None
        ROI volume. Sould be an array with three dimensions.
    labels : array_like | None
        Array of labels. A structured array can be used (i.e
        label=np.zeros(n_sources, dtype=[('brodmann', int), ('aal', object)])).
    index : array_like | None
        Array of index that make the correspondance between the volumne values
        and labels. The length of index must be the same as label.
    hdr : array_like | None
        Array of transform source's coordinates into the volume space. Must be
        a (4, 4) array.
    system : {'mni', 'tal'}
        The system of the volumne. Can either be MNI ('mni') or Talairach
        ('tal').
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        ROI object parent.
    verbose : string
        Verbosity level.
    kw : dict | {}
        Optional arguments are used to control the colorbar
        (See :class:`ColorbarObj`).

    Examples
    --------
    >>> import numpy as np
    >>> from visbrain.objects import RoiObj
    >>> r = RoiObj('brodmann')
    >>> r.select_roi(select=[4, 6, 38], unique_color=True, smooth=7)
    >>> r.preview(axis=True)
    """

    ###########################################################################
    ###########################################################################
    #                                BUILT IN
    ###########################################################################
    ###########################################################################

    def __init__(self, name, vol=None, labels=None, index=None, hdr=None,
                 system='mni', transform=None, parent=None, verbose=None,
                 preload=True, _scale=1., **kw):
        """Init."""
        _Volume.__init__(self, name, parent, transform, verbose, **kw)
        self._scale = _scale
        if preload:
            self(name, vol, labels, index, hdr, system)

    ###########################################################################
    ###########################################################################
    #                                BUILTIN
    ###########################################################################
    ###########################################################################

    def __len__(self):
        """Return the number of ROI."""
        return self._n_roi

    def __call__(self, name, vol=None, labels=None, index=None, hdr=None,
                 system='mni'):
        """Call the set_data method."""
        _Volume.__call__(self, name, vol=vol, labels=labels, index=index,
                         hdr=hdr, system=system)
        self.set_data(name, self._vol, self._labels, self._index, self._hdr,
                      self._system)

    def __bool__(self):
        """Test if ROI have been selected."""
        return hasattr(self, 'mesh')

    def __getitem__(self, index):
        """Get the ref item at index."""
        if isinstance(index, (int, list, np.ndarray, slice)):
            return self.ref.iloc[index]

    def __ge__(self, idx):
        """Test if x >= idx."""
        assert len(idx) == 3
        sh = self._sh
        return (sh[0] >= idx[0]) and (sh[1] >= idx[1]) and (sh[2] >= idx[2])

    def __gt__(self, idx):
        """Test if x > idx."""
        assert len(idx) == 3
        sh = self._sh
        return (sh[0] > idx[0]) and (sh[1] > idx[1]) and (sh[2] > idx[2])

    def __le__(self, idx):
        """Test if x <= idx."""
        assert len(idx) == 3
        sh = self._sh
        return (sh[0] <= idx[0]) and (sh[1] <= idx[1]) and (sh[2] <= idx[2])

    def __lt__(self, idx):
        """Test if x < idx."""
        assert len(idx) == 3
        sh = self._sh
        return (sh[0] < idx[0]) and (sh[1] < idx[1]) and (sh[2] < idx[2])

    ###########################################################################
    ###########################################################################
    #                                SET_DATA
    ###########################################################################
    ###########################################################################

    def set_data(self, name, vol=None, labels=None, index=None, hdr=None,
                 system='mni'):
        """Load an roi object.

        Parameters
        ----------
        name : string
            Name of the ROI object. If name is 'brodmann', 'aal' or
            'talairach' a predefined ROI object is used and vol, index and
            labels are ignored.
        vol : array_like | None
            ROI volume. Sould be an array with three dimensions.
        labels : array_like | None
            Array of labels. A structured array can be used (i.e
            labels=np.zeros(n_sources, dtype=[('brodmann', int),
            ('aal', object)])).
        index : array_like | None
            Array of index that make the correspondance between the volumne
            values and labels. The length of index must be the same as labels.
        hdr : array_like | None
            Array of transform source's coordinates into the volume space.
            Must be a (4, 4) array.
        system : {'mni', 'tal'}
            The system of the volumne. Can either be MNI ('mni') or Talairach
            ('tal').
        """
        # Test if pandas is installed :
        is_pandas_installed(raise_error=True)
        import pandas as pd
        # _______________________ PREDEFINED _______________________
        if not isinstance(vol, np.ndarray):
            vol, labels, index, hdr, system = _Volume.__call__(self, name)
        self._offset = -1 if name == 'talairach' else 0

        # _______________________ CHECKING _______________________
        # vol :
        assert vol.ndim == 3
        # Index and labels :
        assert len(index) == len(labels)
        index = np.asarray(index).astype(int)
        labels = np.asarray(labels)
        self._n_roi = len(index)
        # System :
        assert system in ['mni', 'tal']

        # _______________________ REFERENCE _______________________
        label_dict = self._struct_array_to_dict(labels)
        label_dict['index'] = index
        cols = list(label_dict.keys())
        self.ref = pd.DataFrame(label_dict, columns=cols)
        self.ref = self.ref.set_index(index)
        self.analysis = pd.DataFrame({}, columns=cols)

        logger.info("%s ROI loaded." % name)

    def get_labels(self, save_to_path=None):
        """Get the labels associated with the loaded ROI.

        Parameters
        ----------
        save_to_path : str | None
            Save labels to an excel file.
        """
        if isinstance(save_to_path, str):
            assert os.path.isdir(save_to_path)
            is_pandas_installed(raise_error=True)
            import pandas as pd
            save_as = os.path.join(save_to_path, '%s.xlsx' % self.name)
            writer = pd.ExcelWriter(save_as)
            self.ref.to_excel(writer)
            writer.save()
            logger.info("Saved as %s" % save_as)
        return self.ref

    def where_is(self, patterns, df=None, union=True, columns=None,
                 exact=False):
        """Find a list of string patterns in a DataFrame.

        Parameters
        ----------
        patterns : list
            List of string patterns to search.
        df : pd.DataFrame | None
            The DataFrame to use. If None, the DataFrame of the ROI are going
            to be used by default.
        union : bool | True
            Take either the union of matching patterns (True) or the
            intersection (False).
        columns : list | None
            List of specific column names to search in. If None, this method
            inspect every columns in the DataFrame.
        exact : bool | False
            Specify if the pattern to search have to be exact matching.

        Returns
        -------
        idx : list
            List of index that match with the list of patterns.
        """
        # Check inputs :
        assert isinstance(patterns, (str, list, tuple))
        df_to_use = self.ref if df is None else df
        n_rows, _ = df_to_use.shape
        is_pandas_installed(raise_error=True)
        import pandas as pd
        assert isinstance(df_to_use, pd.DataFrame)
        patterns = [patterns] if isinstance(patterns, str) else patterns
        if columns is None:
            columns = list(df_to_use.keys())
        if isinstance(columns, str):
            columns = [columns]
        assert all([k in df_to_use.keys() for k in columns])
        n_cols = len(columns)
        # Locate patterns :
        idx_to_keep = np.zeros((n_rows, len(patterns)), dtype=bool)
        for p, k in enumerate(patterns):
            pat_in_col = np.zeros((n_rows, n_cols), dtype=bool)
            for c, i in enumerate(columns):
                if exact:
                    pat_in_col[:, c] = df_to_use[i].astype(str) == k
                else:
                    pat_in_col[:, c] = df_to_use[i].astype(str).str.match(k)
            idx_to_keep[:, p] = np.any(pat_in_col, 1)
        # Return either the union or intersection across research :
        if union:
            idx_to_keep = np.any(idx_to_keep, 1)
        else:
            idx_to_keep = np.all(idx_to_keep, 1)
        if not np.any(idx_to_keep):
            logger.error("No corresponding entries in the %s ROI for "
                         "%s" % (self.name, ', '.join(patterns)))
            return []
        else:
            idx_roi = np.array(df_to_use['index'].loc[idx_to_keep]).astype(int)
            return idx_roi.tolist()

    ###########################################################################
    ###########################################################################
    #                                ANALYSE
    ###########################################################################
    ###########################################################################

    def localize_sources(self, xyz, source_name=None, replace_bad=True,
                         bad_patterns=[-1, 'undefined', 'None'],
                         replace_with='Not found', distance=None):
        """Localize source's using this ROI object.

        Parameters
        ----------
        xyz : array_like
            Array of source's coordinates of shape (n_sources, 3)
        source_name : array_like/list | None
            List of source's names.
        replace_bad : bool | True
            Replace bad values (True) or not (False).
        bad_patterns : list | [None, -1, 'undefined', 'None']
            Bad patterns to replace if replace_bad is True.
        replace_with : string | 'Not found'
            Replace bad patterns with this string.
        """
        # Check xyz :
        assert (xyz.ndim == 2) and (xyz.shape[1] == 3)
        xyz_untouched = xyz.copy()
        n_sources = xyz.shape[0]
        if self._system == 'tal':
            xyz = mni2tal(xyz)
        # Check source_name :
        if source_name is None:
            source_name = ['s' + str(k) for k in range(n_sources)]
        assert len(source_name) == n_sources
        # Loop over sources :
        for k in range(n_sources):
            # Apply HDR transformation :
            sub = self.pos_to_slice(xyz[k, :])
            # Find where is the point if inside the volume :
            if self > sub:  # use __gt__ of RoiObj
                idx_vol = self._vol[sub[0], sub[1], sub[2]] + self._offset
                location = self._find_roi_label(idx_vol)
            else:
                location = None
            self.analysis.loc[k] = location
        # Replace bad patterns :
        if replace_bad:
            # Replace NaN values :
            self.analysis.fillna(replace_with, inplace=True)
            # Replace bad patterns :
            for k in bad_patterns:
                self.analysis.replace(k, replace_with, inplace=True)
        # Replace unfound informations with the closest source info :
        if isinstance(distance, (int, float)):
            distance = float(distance)
            # Find rows that contains the replace_with pattern :
            bad_rows = []
            analyse_cols = [k for k in self.analysis.keys() if self.analysis[
                k].dtype == object]
            for k in analyse_cols:
                bad_rows.append(self.analysis[k] == replace_with)
            bad_rows = np.where(np.array(bad_rows).sum(0))[0]
            good_rows = np.arange(n_sources)
            good_rows = np.delete(good_rows, bad_rows)
            logger.info("%i rows containing the %r pattern "
                        "found" % (len(bad_rows), replace_with))
            # Get good and bad xyz and compute euclidian distance :
            xyz_good = xyz_untouched[good_rows, :]
            xyz_bad = xyz_untouched[bad_rows, :]
            xyz_dist = cdist(xyz_bad, xyz_good)
            xyz_dist_bool = np.any(xyz_dist <= distance, axis=1)
            close_str = np.array(["None under %.1f" % distance] * n_sources)
            n_replaced = 0
            if np.any(xyz_dist_bool):
                for k in np.where(xyz_dist_bool)[0]:
                    close_idx = good_rows[xyz_dist[k, :].argmin()]
                    bad_row = bad_rows[k]
                    self.analysis.loc[bad_row] = self.analysis.loc[close_idx]
                    close_str[bad_row] = source_name[close_idx]
                    n_replaced += 1
            close_str[good_rows] = -1
            self.analysis["Replaced with"] = close_str
            logger.info("Anatomical informations of %i sources have been "
                        "replaced using a distance of "
                        "%1.f" % (n_replaced, distance))
        # Add Text and (X, Y, Z) to the table :
        new_col = ['Text'] + self.analysis.columns.tolist() + ['X', 'Y', 'Z']
        self.analysis['Text'] = source_name
        self.analysis['X'] = xyz_untouched[:, 0]
        self.analysis['Y'] = xyz_untouched[:, 1]
        self.analysis['Z'] = xyz_untouched[:, 2]
        self.analysis = self.analysis[new_col]
        # Add hemisphere to the dataframe :
        hemisphere = np.array(['Left'] * xyz_untouched.shape[0], dtype=object)
        hemisphere[xyz_untouched[:, 0] > 0] = 'Right'
        self.analysis['hemisphere'] = hemisphere
        return self.analysis

    def _find_roi_label(self, vol_idx):
        """Find the ROI label associated to a volume index."""
        ref_index = np.where(self.ref['index'] == vol_idx)[0]
        return self[int(ref_index[0])] if ref_index.size else None

    @staticmethod
    def _struct_array_to_dict(arr):
        """Convert a structured array into a dictionnary."""
        try:
            if arr.dtype.names is None:
                return {'label': arr}
            else:
                return {k: arr[k] for k in arr.dtype.names}
        except:
            return {'label': arr}

    @staticmethod
    def _df_to_struct_array(df):
        """Convert a pandas DataFrame object to a numpy structured array.

        Credit to :
        https://stackoverflow.com/questions/13187778/convert-pandas-dataframe-
        to-numpy-array-preserving-index
        """
        # Get data and column names :
        v = df.values
        cols = df.columns
        # Build the struct array :
        types = [(cols[i], df[k].dtype.type) for (i, k) in enumerate(cols)]
        dtype = np.dtype(types)
        z = np.zeros(v.shape[0], dtype)
        for (i, k) in enumerate(z.dtype.names):
            z[k] = v[:, i]
        return z

    ###########################################################################
    ###########################################################################
    #                                MESH
    ###########################################################################
    ###########################################################################

    def select_roi(self, select=.5, unique_color=False, roi_to_color=None,
                   smooth=3):
        """Select several Region Of Interest (ROI).

        Parameters
        ----------
        select : int, float, list | .5
            Threshold for extracting vertices from isosuface method.
        unique_color : bool | False
            Use a random unique color for each ROI.
        roi_to_color : dict | None
            Color of specific ROI using a dictionary i.e
            {1: 'red', 2: 'orange'}.
        smooth : int | 3
            Smoothing level. Must be an odd integer (smooth % 2 = 1).
        """
        # Get vertices / faces :
        vert = np.array([])
        # Use specific colors :
        if isinstance(roi_to_color, dict):
            select = roi_to_color.keys()
            unique_color = True
        if not unique_color:
            vert, faces = self._select_roi(self._vol.copy(), select, smooth)
            logger.info("Same white color used across ROI(s)")
        else:
            assert not isinstance(select, float)
            select = [select] if isinstance(select, int) else select
            vert, faces, color = np.array([]), np.array([]), np.array([])
            # Generate a (n_levels, 4) array of unique colors :
            if isinstance(roi_to_color, dict):
                assert len(roi_to_color) == len(select)
                col_unique = [color2vb(k) for k in roi_to_color.values()]
                col_unique = np.array(col_unique).reshape(len(select), 4)
                logger.info("Specific colors has been defined")
            else:
                col_unique = np.random.uniform(.1, .9, (len(select), 4))
                col_unique[..., -1] = 1.
                logger.info("Random color are going to be used.")
            # Get vertices and faces of each ROI :
            for i, k in enumerate(select):
                v, f = self._select_roi(self._vol.copy(), int(k), smooth)
                # Concatenate vertices / faces :
                faces = np.r_[faces, f + faces.max() + 1] if faces.size else f
                vert = np.r_[vert, v] if vert.size else v
                # Concatenate color :
                col = np.tile(col_unique[[i], ...], (v.shape[0], 1))
                color = np.r_[color, col] if color.size else col
        if vert.size:
            # Apply hdr transformation to vertices :
            vert_hdr = self._hdr.map(vert)[:, 0:-1]
            logger.debug("Apply hdr transformation to vertices")
            if not self:
                logger.debug("ROI mesh defined")
                self.mesh = BrainMesh(vertices=vert_hdr, faces=faces,
                                      parent=self._node)
            else:
                logger.debug("ROI mesh already exist")
                self.mesh.set_data(vertices=vert_hdr, faces=faces)
            if unique_color:
                self.mask = 1.
                self.color = color
        else:
            raise ValueError("No vertices found for this ROI")

    def _select_roi(self, vol, level, smooth):
        if isinstance(level, (int, np.int)):
            condition = vol != level
        elif isinstance(level, float):
            condition = vol < level
        elif isinstance(level, (np.ndarray, list, tuple)):
            condition = np.logical_and.reduce([vol != k for k in level])
        # Set unused ROIs to 0 in the volume :
        vol[condition] = 0
        # Get the list of remaining ROIs :
        unique_vol = np.unique(vol[vol != 0])
        logger.info("Selected ROI(s) : \n%r" % self.ref.loc[unique_vol])
        return isosurface(smooth_3d(vol, smooth), level=.5)

    def _get_camera(self):
        """Get the most adapted camera."""
        if not self:
            logger.warning("Every ROI selected. Use the method `select_roi` "
                           "before to control the ROI to display.")
            self.select_roi()
        self.mesh.set_camera(scene.cameras.TurntableCamera())
        sc = self.mesh._opt_cam_state['scale_factor'][-1] * self._scale
        center = self.mesh._opt_cam_state['center'] * self._scale
        self.mesh._camera.scale_factor = sc
        self.mesh._camera.distance = 4 * sc
        self.mesh._camera.center = center
        return self.mesh._camera

    ###########################################################################
    ###########################################################################
    #                                PROJECTION
    ###########################################################################
    ###########################################################################

    def project_sources(self, s_obj, project='modulation', radius=10.,
                        contribute=False, cmap='viridis', clim=None, vmin=None,
                        under='black', vmax=None, over='red',
                        mask_color=None):
        """Project source's activity or repartition onto ROI.

        Parameters
        ----------
        s_obj : SourceObj
            The source object to project.
        project : {'modulation', 'repartition'}
            Project either the source's data ('modulation') or get the number
            of contributing sources per vertex ('repartition').
        radius : float
            The radius under which activity is projected on vertices.
        contribute: bool | False
            Specify if sources contribute on both hemisphere.
        cmap : string | 'viridis'
            The colormap to use.
        clim : tuple | None
            The colorbar limits. If None, (data.min(), data.max()) will be used
            instead.
        vmin : float | None
            Minimum threshold.
        vmax : float | None
            Maximum threshold.
        under : string/tuple/array_like | 'gray'
            The color to use for values under vmin.
        over : string/tuple/array_like | 'red'
            The color to use for values over vmax.
        mask_color : string/tuple/array_like | 'gray'
            The color to use for the projection of masked sources. If None,
            the color of the masked sources is going to be used.
        """
        if self:
            kw = self._update_cbar_args(cmap, clim, vmin, vmax, under, over)
            self._default_cblabel = "Source's %s" % project
            _project_sources_data(s_obj, self, project, radius, contribute,
                                  mask_color=mask_color, **kw)
        else:
            raise ValueError("Cannot project sources because no ROI selected. "
                             "Use the `select_roi` method before.")

    ###########################################################################
    ###########################################################################
    #                                PROPERTIES
    ###########################################################################
    ###########################################################################

    # ----------- TRANSLUCENT -----------
    @property
    @wrap_getter_properties
    def translucent(self):
        """Get the translucent value."""
        return self.mesh.translucent

    @translucent.setter
    @wrap_setter_properties
    def translucent(self, value):
        """Set translucent value."""
        self.mesh.translucent = value

    # ----------- ALPHA -----------
    @property
    @wrap_getter_properties
    def alpha(self):
        """Get the alpha value."""
        return self.mesh.alpha

    @alpha.setter
    @wrap_setter_properties
    def alpha(self, value):
        """Set alpha value."""
        self.mesh.alpha = value

    # ----------- VERTICES -----------
    @property
    @wrap_getter_properties
    def vertices(self):
        """Get the vertices value."""
        return self.mesh._vertices

    # ----------- FACES -----------
    @property
    @wrap_getter_properties
    def faces(self):
        """Get the faces value."""
        return self.mesh._faces

    # ----------- NORMALS -----------
    @property
    @wrap_getter_properties
    def normals(self):
        """Get the normals value."""
        return self.mesh._normals

    # ----------- MASK -----------
    @property
    @wrap_getter_properties
    def mask(self):
        """Get the mask value."""
        return self.mesh.mask

    @mask.setter
    @wrap_setter_properties
    def mask(self, value):
        """Set mask value."""
        self.mesh.mask = value

    # ----------- COLOR -----------
    @property
    @wrap_getter_properties
    def color(self):
        """Get the color value."""
        return self.mesh.color

    @color.setter
    @wrap_setter_properties
    def color(self, value):
        """Set color value."""
        self.mesh.color = value

    # ----------- MASK_COLOR -----------
    @property
    @wrap_getter_properties
    def mask_color(self):
        """Get the mask_color value."""
        return self.mesh.mask_color

    @mask_color.setter
    @wrap_setter_properties
    def mask_color(self, value):
        """Set mask_color value."""
        self.mesh.mask_color = value

    # ----------- CAMERA -----------
    @property
    def camera(self):
        """Get the camera value."""
        return self._camera

    @camera.setter
    @wrap_setter_properties
    def camera(self, value):
        """Set camera value."""
        self.mesh.set_camera(value)


class CombineRoi(_CombineVolume):
    """Combine Roi objects.

    Parameters
    ----------
    robjs : RoiObj/list | None
        List of Roi objects.
    select : string | None
        The name of the Roi object to select.
    parent : VisPy.parent | None
        Roi object parent.
    """

    def __init__(self, robjs=None, select=None, parent=None):
        """Init."""
        _CombineVolume.__init__(self, RoiObj, robjs, select, parent)

    # ----------- CAMERA -----------
    @property
    def camera(self):
        """Get the camera value."""
        return self._camera

    @camera.setter
    def camera(self, value):
        """Set camera value."""
        for k in self:
            k.mesh.set_camera(value)
