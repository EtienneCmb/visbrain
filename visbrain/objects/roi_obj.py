"""Base class for objects of type ROI."""
import logging
from functools import wraps
import numpy as np

from vispy import scene
from vispy.geometry.isosurface import isosurface

from .visbrain_obj import CombineObjects
from .volume_obj import _Volume
from ._projection import _project_sources_data
from ..io import is_pandas_installed
from ..utils import mni2tal, smooth_3d, color2vb, array_to_stt
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
    label : array_like | None
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
    >>> r.select_roi(level=[4, 6, 38], unique_color=True, plot=True,
    >>>              smooth=7)
    >>> r.preview(axis=True)
    """

    ###########################################################################
    ###########################################################################
    #                                BUILT IN
    ###########################################################################
    ###########################################################################

    def __init__(self, name, vol=None, label=None, index=None, hdr=None,
                 system='mni', transform=None, parent=None, verbose=None,
                 preload=True, _scale=1., **kw):
        """Init."""
        _Volume.__init__(self, name, parent, transform, verbose, **kw)
        self._scale = _scale
        if preload and (name in self._predefined_volumes()):
            self.set_data(name, vol, label, index, hdr, system)

    ###########################################################################
    ###########################################################################
    #                                BUILTIN
    ###########################################################################
    ###########################################################################

    def __len__(self):
        """Return the number of ROI."""
        return self._n_roi

    def __call__(self, name):
        """Call the set_data method."""
        self.set_data(name)

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
        sh = self.vol.shape
        return (sh[0] >= idx[0]) and (sh[1] >= idx[1]) and (sh[2] >= idx[2])

    def __gt__(self, idx):
        """Test if x > idx."""
        assert len(idx) == 3
        sh = self.vol.shape
        return (sh[0] > idx[0]) and (sh[1] > idx[1]) and (sh[2] > idx[2])

    def __le__(self, idx):
        """Test if x <= idx."""
        assert len(idx) == 3
        sh = self.vol.shape
        return (sh[0] <= idx[0]) and (sh[1] <= idx[1]) and (sh[2] <= idx[2])

    def __lt__(self, idx):
        """Test if x < idx."""
        assert len(idx) == 3
        sh = self.vol.shape
        return (sh[0] < idx[0]) and (sh[1] < idx[1]) and (sh[2] < idx[2])

    ###########################################################################
    ###########################################################################
    #                                SET_DATA
    ###########################################################################
    ###########################################################################

    def set_data(self, name, vol=None, label=None, index=None, hdr=None,
                 system='mni'):
        """Load an roi object.

        Parameters
        ----------
        name : string
            Name of the ROI object. If name is 'brodmann', 'aal' or
            'talairach' a predefined ROI object is used and vol, index and
            label are ignored.
        vol : array_like | None
            ROI volume. Sould be an array with three dimensions.
        label : array_like | None
            Array of labels. A structured array can be used (i.e
            label=np.zeros(n_sources, dtype=[('brodmann', int),
            ('aal', object)])).
        index : array_like | None
            Array of index that make the correspondance between the volumne
            values and labels. The length of index must be the same as label.
        hdr : array_like | None
            Array of transform source's coordinates into the volume space.
            Must be a (4, 4) array.
        system : {'mni', 'tal'}
            The system of the volumne. Can either be MNI ('mni') or Talairach
            ('tal').
        """
        # Test if pandas is installed :
        if not is_pandas_installed():
            raise ImportError("In order to work properly, pandas package "
                              "should be installed using *pip install pandas*")
        import pandas as pd
        # _______________________ PREDEFINED _______________________
        if name in ['brodmann', 'talairach', 'aal']:
            vol, label, index, hdr, system = _Volume.__call__(self, name)
        self._offset = -1 if name == 'talairach' else 0

        # _______________________ CHECKING _______________________
        # vol :
        assert vol.ndim == 3
        # Index and label :
        assert len(index) == len(label)
        index = np.asarray(index).astype(int)
        label = np.asarray(label)
        self.vol = vol
        self._n_roi = len(index)
        # hdr :
        self.hdr = np.eye(4) if hdr is None else hdr
        assert self.hdr.shape == (4, 4)
        # System :
        assert system in ['mni', 'tal']
        self.system = system

        # _______________________ REFERENCE _______________________
        label_dict = self._struct_array_to_dict(label)
        label_dict['index'] = index
        cols = list(label_dict.keys())
        self.ref = pd.DataFrame(label_dict, columns=cols)
        self.ref = self.ref.set_index(index)
        self.analysis = pd.DataFrame({}, columns=cols)

        logger.info("%s ROI loaded." % name)

    def get_labels(self):
        """Get the labels associated with the loaded ROI."""
        return self.ref

    ###########################################################################
    ###########################################################################
    #                                ANALYSE
    ###########################################################################
    ###########################################################################

    def localize_sources(self, xyz, source_name=None, replace_bad=True,
                         bad_patterns=[-1, 'undefined', 'None'],
                         replace_with='Not found'):
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
        if self.system == 'tal':
            xyz = mni2tal(xyz)
        # Check source_name :
        if source_name is None:
            source_name = ['s' + str(k) for k in range(n_sources)]
        assert len(source_name) == n_sources
        # Loop over sources :
        xyz = np.c_[xyz, np.ones((n_sources,), dtype=xyz.dtype)].T
        for k in range(n_sources):
            # Apply HDR transformation :
            pos = np.linalg.lstsq(self.hdr, xyz[:, k])[0][0:-1]
            sub = np.round(pos).astype(int)
            # Find where is the point if inside the volume :
            if self >= sub:  # use __ge__ of RoiObj
                idx_vol = self.vol[sub[0], sub[1], sub[2]] + self._offset
                location = self._find_roi_label(idx_vol)
            else:
                location = None
            self.analysis.loc[k] = location
        if replace_bad:
            # Replace NaN values :
            self.analysis.fillna(replace_with, inplace=True)
            # Replace bad patterns :
            for k in bad_patterns:
                self.analysis.replace(k, replace_with, inplace=True)
        # Add Text and (X, Y, Z) to the table :
        new_col = ['Text'] + self.analysis.columns.tolist() + ['X', 'Y', 'Z']
        self.analysis['Text'] = source_name
        self.analysis['X'] = xyz_untouched[:, 0]
        self.analysis['Y'] = xyz_untouched[:, 1]
        self.analysis['Z'] = xyz_untouched[:, 2]
        self.analysis = self.analysis[new_col]
        # Add hemisphere to the dataframe :
        hemisphere = np.array(['Left'] * xyz_untouched.shape[0])
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
            vert, faces = self._select_roi(self.vol, select, smooth)
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
                v, f = self._select_roi(self.vol, k, smooth)
                # Concatenate vertices / faces :
                faces = np.r_[faces, f + faces.max() + 1] if faces.size else f
                vert = np.r_[vert, v] if vert.size else v
                # Concatenate color :
                col = np.tile(col_unique[[i], ...], (v.shape[0], 1))
                color = np.r_[color, col] if color.size else col
        if vert.size:
            # Apply hdr transformation to vertices :
            vert = array_to_stt(self.hdr).map(vert)[:, 0:-1]
            logger.debug("Apply hdr transformation to vertices")
            if not self:
                logger.debug("ROI mesh defined")
                self.mesh = BrainMesh(vertices=vert, faces=faces,
                                      parent=self._node)
            else:
                logger.debug("ROI mesh already exist")
                self.mesh.set_data(vertices=vert, faces=faces)
            if unique_color:
                self.mask = 1.
                self.color = color
        else:
            raise ValueError("No vertices found for this ROI")

    def _select_roi(self, vol, level, smooth):
        vol = vol.copy()
        if isinstance(level, int):
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
        return self._normals

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


class CombineRoi(CombineObjects):
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
        CombineObjects.__init__(self, RoiObj, robjs, select, parent)
