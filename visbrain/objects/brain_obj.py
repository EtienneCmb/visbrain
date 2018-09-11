"""Base class for objects of type brain."""
import os
import numpy as np
import logging

from vispy import scene

from .visbrain_obj import VisbrainObject
from ._projection import _project_sources_data
from ..visuals import BrainMesh
from ..utils import (mesh_edges, smoothing_matrix, rotate_turntable)
from ..io import (is_nibabel_installed, is_pandas_installed,
                  add_brain_template, remove_brain_template)

logger = logging.getLogger('visbrain')


class BrainObj(VisbrainObject):
    """Create a brain object.

    Parameters
    ----------
    name : string
        Name of the brain object. If brain is 'B1' or 'B2' or 'B3' use a
        default brain template. If name is 'white', 'inflated' or
        'sphere' download the template (if needed). Otherwise, at least
        vertices and faces must be defined.
    vertices : array_like | None
        Mesh vertices to use for the brain. Must be an array of shape
        (n_vertices, 3).
    faces : array_like | None
        Mesh faces of shape (n_faces, 3).
    normals : array_like | None
        Normals to each vertex. If None, the program will try to compute it.
        Must be an array with the same shape as vertices.
    lr_index : array_like | None
        Left / Right index for hemispheres. Must be a vector of length
        n_vertices. This vector must be a boolean array where True refer to
        vertices that belong to the left hemisphere and False, the right
        hemisphere.
    hemisphere : {'left', 'both', 'right'}
        The hemisphere to plot.
    translucent : bool | True
        Use translucent (True) or opaque (False) brain.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Brain object parent.
    verbose : string
        Verbosity level.
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
    >>> from visbrain.objects import BrainObj
    >>> b = BrainObj('white', hemisphere='right', translucent=False)
    >>> b.preview(axis=True)
    """

    ###########################################################################
    ###########################################################################
    #                                BUILT IN
    ###########################################################################
    ###########################################################################

    def __init__(self, name, vertices=None, faces=None, normals=None,
                 lr_index=None, hemisphere='both', translucent=True,
                 sulcus=False, invert_normals=False, transform=None,
                 parent=None, verbose=None, _scale=1., **kw):
        """Init."""
        # Init Visbrain object base class :
        VisbrainObject.__init__(self, name, parent, transform, verbose, **kw)
        # Load brain template :
        self._scale = _scale
        self.data_folder = 'templates'
        self.set_data(name, vertices, faces, normals, lr_index, hemisphere,
                      invert_normals, sulcus)
        self.translucent = translucent

    def __len__(self):
        """Get the number of vertices."""
        return self.vertices.shape[0]

    def set_data(self, name=None, vertices=None, faces=None, normals=None,
                 lr_index=None, hemisphere='both', invert_normals=False,
                 sulcus=False):
        """Load a brain template."""
        # _______________________ TEMPLATE _______________________
        if not all([isinstance(k, np.ndarray) for k in [vertices, faces]]):
            to_load = None
            name_npz = name + '.npz'
            # Identify if the template is already downloaded or not :
            if name in self._df_get_downloaded():
                to_load = self._df_get_file(name_npz, download=False)
            elif name_npz in self._df_get_downloadable():  # need download
                to_load = self._df_download_file(name_npz)
            assert isinstance(to_load, str)
            # Load the template :
            arch = np.load(to_load)
            vertices, faces = arch['vertices'], arch['faces']
            normals = arch['normals']
            lr_index = arch['lr_index'] if 'lr_index' in arch.keys() else None

        # Sulcus :
        if sulcus is True:
            if not self._df_is_downloaded('sulcus.npy'):
                sulcus_file = self._df_download_file('sulcus.npy')
            else:
                sulcus_file = self._df_get_file('sulcus.npy')
            sulcus = np.load(sulcus_file)
        else:
            sulcus = None
        # _______________________ CHECKING _______________________
        assert all([isinstance(k, np.ndarray) for k in (vertices, faces)])
        if normals is not None:  # vertex normals
            assert isinstance(normals, np.ndarray)
        assert (lr_index is None) or isinstance(lr_index, np.ndarray)
        assert hemisphere in ['both', 'left', 'right']
        if isinstance(sulcus, np.ndarray) and len(sulcus) != vertices.shape[0]:
            logger.error("Sulcus ignored. Use it only for the inflated, white "
                         "and sphere brain templates")
            sulcus = None

        self._define_mesh(vertices, faces, normals, lr_index, hemisphere,
                          invert_normals, sulcus)

    def clean(self):
        """Clean brain object."""
        self.hemisphere = 'both'
        self.rotate('top')
        logger.info("    Brain object %s cleaned." % self.name)

    def save(self, tmpfile=False):
        """Save the brain template (if not already saved)."""
        save_as = self.name + '.npz'
        v = self.mesh._vertices
        f = self.mesh._faces
        n = self.mesh._normals
        lr = self.mesh._lr_index
        add_brain_template(save_as, v, f, normals=n, lr_index=lr,
                           tmpfile=tmpfile)

    def remove(self):
        """Remove a brain template."""
        remove_brain_template(self.name + '.npz')

    def list(self, file=None):
        """Get the list of all installed templates."""
        return self._df_get_downloaded(with_ext=False, exclude=['sulcus'])

    def _define_mesh(self, vertices, faces, normals, lr_index, hemisphere,
                     invert_normals, sulcus):
        """Define brain mesh."""
        if not hasattr(self, 'mesh'):
            # Mesh brain :
            self.mesh = BrainMesh(vertices=vertices, faces=faces,
                                  normals=normals, lr_index=lr_index,
                                  hemisphere=hemisphere, parent=self._node,
                                  invert_normals=invert_normals, sulcus=sulcus,
                                  name='Mesh')
        else:
            self.mesh.set_data(vertices=vertices, faces=faces, normals=normals,
                               lr_index=lr_index, hemisphere=hemisphere)

    ###########################################################################
    ###########################################################################
    #                           CAMERA // ROTATION
    ###########################################################################
    ###########################################################################

    def _get_camera(self):
        """Get the most adapted camera."""
        if self.mesh._camera is None:
            self.camera = scene.cameras.TurntableCamera(name='BrainTurntable')
            self.rotate('top')
        return self.camera

    def reset_camera(self):
        """Reset the camera."""
        # Get the optimal camera for the mesh :
        cam_state = self.mesh._opt_cam_state.copy()
        # Re-scale (OpenGL issue) :
        cam_state['center'] *= self._scale
        cam_state['scale_factor'] = cam_state['scale_factor'][-1] * self._scale
        cam_state.update({'azimuth': 0., 'elevation': 90})
        # Set distance :
        distance = cam_state['scale_factor'] * 4.
        self.mesh._camera.distance = distance
        # Set camera :
        self.mesh._camera.set_state(cam_state)
        self.mesh._camera.set_default_state()

    def rotate(self, fixed=None, scale_factor=None, custom=None, margin=1.08):
        """Rotate the brain using predefined rotations or a custom one.

        Parameters
        ----------
        fixed : str | 'top'
            Use a fixed rotation :

                * Top view : 'axial_0', 'top'
                * Bottom view : 'axial_1', 'bottom'
                * Left : 'sagittal_0', 'left'
                * Right : 'sagittal_1', 'right'
                * Front : 'coronal_0', 'front'
                * Back : 'coronal_1', 'back'
        custom : tuple | None
            Custom rotation. This parameter must be a tuple of two floats
            respectively describing the (azimuth, elevation).
        """
        # Create the camera if needed :
        self._get_camera()
        cam_state = self.mesh._opt_cam_state.copy()
        xyz = cam_state['scale_factor']
        if isinstance(scale_factor, (int, float)):
            cam_state['scale_factor'] = scale_factor
        if isinstance(custom, (tuple, list)) and (len(custom) == 2):
            cam_state['azimuth'] = custom[0]
            cam_state['elevation'] = custom[1]
            is_sc_float = isinstance(cam_state['scale_factor'], (int, float))
            if 'scale_factor' in cam_state.keys() and not is_sc_float:
                del cam_state['scale_factor']
            self.camera.set_state(**cam_state)
        else:
            rotate_turntable(fixed, cam_state, camera=self.camera, xyz=xyz,
                             csize=self._csize, margin=margin,
                             _scale=self._scale)

    ###########################################################################
    ###########################################################################
    #                             PROJECTIONS
    ###########################################################################
    ###########################################################################

    def project_sources(self, s_obj, project='modulation', radius=10.,
                        contribute=False, cmap='viridis', clim=None, vmin=None,
                        under='black', vmax=None, over='red',
                        mask_color=None, to_overlay=0):
        """Project source's activity or repartition onto the brain object.

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
        kw = self._update_cbar_args(cmap, clim, vmin, vmax, under, over)
        self._default_cblabel = "Source %s" % project
        _project_sources_data(s_obj, self, project, radius, contribute,
                              mask_color=mask_color, to_overlay=to_overlay,
                              **kw)

    def add_activation(self, data=None, vertices=None, smoothing_steps=5,
                       file=None, hemisphere=None, hide_under=None,
                       n_contours=None, cmap='viridis', clim=None, vmin=None,
                       vmax=None, under='gray', over='red'):
        """Add activation to the brain template.

        This method can be used for :

            * Add activations to specific vertices (`data` and `vertices`)
            * Add an overlay (`file` input)

        Parameters
        ----------
        data : array_like | None
            Vector array of data of shape (n_data,).
        vertices : array_like | None
            Vector array of vertex indices of shape (n_vtx).
            Must be an array of integers. If hemisphere is 'left' or 'right'
            indexation is done with respect to the specified hemisphere.
        smoothing_steps : int | 20
            Number of smoothing steps (smoothing is used if n_data < n_vtx).
            If None or 0, no smoothing is performed.
        file : string | None
            Full path to the overlay file.
        hemisphrere : {None, 'both', 'left', 'right'}
            The hemisphere to use to add the overlay. If None, the method tries
            to infer the hemisphere from the file name.
        hide_under : float | None
            Hide activations under a certain threshold.
        n_contours : int | None
            Display activations as contour.
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
        """
        kw = self._update_cbar_args(cmap, clim, vmin, vmax, under, over)
        is_under = isinstance(hide_under, (int, float))
        mask = np.zeros((len(self.mesh),), dtype=bool)
        data_vec = np.zeros((len(self.mesh),), dtype=np.float32)
        sm_data = np.zeros((len(self.mesh),), dtype=np.float32)
        self._default_cblabel = "Activation"
        # ============================= METHOD =============================
        if isinstance(data, np.ndarray):
            # Hemisphere :
            hemisphere, activ_vert = self._hemisphere_from_file(hemisphere,
                                                                file)
            activ_vert_idx = np.where(activ_vert)[0]

            is_do_smoothing = True

            if vertices is None:
                # Data are defined on a dense grid
                assert len(activ_vert_idx) == len(data)
                vertices = np.arange(len(activ_vert_idx))
                is_do_smoothing = False
                if smoothing_steps:
                    logger.warning(
                        'Data defined on a dense grid; ignore smoothing.')
            else:
                assert len(vertices) == len(data)

            logger.info("    Add data to specific vertices.")
            assert (data.ndim == 1) and (np.asarray(vertices).ndim == 1)
            assert smoothing_steps is None or isinstance(smoothing_steps, int)

            # Get smoothed vertices // data :
            if hemisphere != 'both':
                # Transform to indexing with respect to the whole brain
                vert_whole = activ_vert_idx[vertices]
            else:
                vert_whole = vertices

            if smoothing_steps and is_do_smoothing:
                edges = mesh_edges(self.mesh._faces)
                sm_mat = smoothing_matrix(vert_whole, edges, smoothing_steps)
                sc = sm_mat * data  # actual data smoothing
                if hemisphere != 'both':
                    sc = sc[activ_vert]
            else:
                sc = np.zeros_like(sm_data[activ_vert])
                sc[vertices] = data
        elif isinstance(file, str):
            assert os.path.isfile(file)
            logger.info("    Add overlay to the {} brain template "
                        "({})".format(self._name, file))
            from visbrain.io import read_nifti
            # Load data using Nibabel :
            sc, _, _ = read_nifti(file)
            sc = sc.ravel(order="F")
            hemisphere = 'both' if len(sc) == len(self.mesh) else hemisphere
            # Hemisphere :
            _, activ_vert = self._hemisphere_from_file(hemisphere, file)
        else:
            raise ValueError("Unknown activation type.")
        # Define the data to send to the vertices :
        sm_data[activ_vert] = sc
        data_vec[activ_vert] = self._data_to_contour(sc, clim, n_contours)
        mask[activ_vert] = True
        # Hide under :
        if is_under:
            mask[sm_data < hide_under] = False
        # Clim :
        clim = (sc.min(), sc.max()) if clim is None else clim
        assert len(clim) == 2
        kw['clim'] = clim
        # Add overlay :
        self.mesh.add_overlay(data_vec[mask], vertices=np.where(mask)[0], **kw)

    def parcellize(self, file, select=None, hemisphere=None, data=None,
                   cmap='viridis', clim=None, vmin=None, under='gray',
                   vmax=None, over='red'):
        """Parcellize the brain surface using a .annot file.

        This method require the nibabel package to be installed.

        Parameters
        ----------
        file : string
            Path to the .annot file.
        select : array_like | None
            Select the structures to display. Use either a list a index or a
            list of structure's names. If None, all structures are displayed.
        hemisphere : string | None
            The hemisphere for the parcellation. If None, the hemisphere will
            be inferred from file name.
        data : array_like | None
            Use data to be transformed into color for each parcellate.
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
        """
        idx, u_colors, labels, u_idx = self._load_annot_file(file)
        roi_labs = []
        kw = self._update_cbar_args(cmap, clim, vmin, vmax, under, over)
        data_vec = np.zeros((len(self.mesh),), dtype=np.float32)
        # Get the hemisphere and (left // right) boolean index :
        hemisphere, h_idx = self._hemisphere_from_file(hemisphere, file)
        # Select conversion :
        if select is None:
            logger.info("    Select all parcellates")
            select = labels.tolist()
            if 'Unknown' in select:
                select.pop(select.index('Unknown'))
        # Manage color if data is an array :
        if isinstance(data, (np.ndarray, list, tuple)):
            data = np.asarray(data)
            assert data.ndim == 1 and len(data) == len(select)
            clim = (data.min(), data.max()) if clim is None else clim
            kw = self._update_cbar_args(cmap, clim, vmin, vmax, under, over)
            logger.info("    Color inferred from data")
            u_colors = np.zeros((len(u_idx), 4), dtype=float)
            self._default_cblabel = "Parcellates data"
        else:
            logger.info("    Use default color included in the file")
            u_colors = u_colors.astype(float) / 255.
        # Build the select variable :
        if isinstance(select, (np.ndarray, list)):
            select = np.asarray(select)
            if select.dtype != int:
                logger.info('    Search parcellates using labels')
                select_str = select.copy()
                select, bad_select = [], []
                for k in select_str:
                    label_idx = np.where(labels == k)[0]
                    if label_idx.size:
                        select.append(u_idx[label_idx])
                    else:
                        roi_labs.append('%s (ignored)' % k)
                        bad_select.append(k)
                if len(bad_select):
                    logger.warning("%s ignored. Use `get_parcellates` method "
                                   "to get the list of available "
                                   "parcellates" % ', '.join(bad_select))
                select = np.array(select).ravel()
        if not select.size:
            raise ValueError("No parcellates found")
        # Get corresponding hemisphere indices (left, right or both) :
        hemi_idx = np.where(h_idx)[0]
        # Prepare color variables :
        color = []
        mask = np.zeros((len(self.mesh),), dtype=bool)
        # Set roi color to the mesh :
        no_parcellates = []
        for i, k in enumerate(select):
            sub_idx = np.where(u_idx == k)[0][0]  # index location in u_idx
            if sub_idx:
                vert_index = hemi_idx[u_idx[idx] == k]
                color.append(u_colors[sub_idx, :])
                roi_labs.append(labels[sub_idx])
                mask[vert_index] = True
                data_vec[vert_index] = data[i] if data is not None else i
            else:
                no_parcellates.append(str(k))
        if no_parcellates:
            logger.warning("No corresponding parcellates for index "
                           "%s" % ', '.join(np.unique(no_parcellates)))
        if data is None:
            color = np.asarray(color, dtype=np.float32)
            kw['cmap'] = color[:, 0:-1]
            kw['interpolation'] = 'linear'
        logger.info("    Selected parcellates : %s" % ", ".join(roi_labs))
        # Finally, add the overlay to the brain :
        self.mesh.add_overlay(data_vec[mask], vertices=np.where(mask)[0], **kw)

    def get_parcellates(self, file):
        """Get the list of supported parcellates names and index.

        This method require the pandas and nibabel packages to be installed.

        Parameters
        ----------
        file : string
            Path to the .annot file.
        """
        is_pandas_installed(raise_error=True)
        import pandas as pd
        _, color, labels, u_idx = self._load_annot_file(file)
        dico = dict(Index=u_idx, Labels=labels, Color=color.tolist())
        return pd.DataFrame(dico, columns=['Index', 'Labels', 'Color'])

    def slice(self, xmin=None, xmax=None, ymin=None, ymax=None, zmin=None,
              zmax=None):
        """Take a slice of the brain.

        Parameters
        ----------
        xmin, xmax : float | None
            Cut the mesh along the x-dimension.
        ymin, ymax : float | None
            Cut the mesh along the y-dimension.
        zmin, zmax : float | None
            Cut the mesh along the z-dimension.
        """
        self.mesh.xmin = xmin
        self.mesh.xmax = xmax
        self.mesh.ymin = ymin
        self.mesh.ymax = ymax
        self.mesh.zmin = zmin
        self.mesh.zmax = zmax

    @staticmethod
    def _data_to_contour(data, clim, n_contours):
        clim = (data.min(), data.max()) if clim is None else clim
        if isinstance(n_contours, int):
            _range = np.linspace(clim[0], clim[1], n_contours)
            for k in range(len(_range) - 1):
                d_idx = np.logical_and(data >= _range[k], data < _range[k + 1])
                data[d_idx] = _range[k]
        return data

    def _hemisphere_from_file(self, hemisphere, file):
        """Infer hemisphere from filename."""
        if (hemisphere is None) and isinstance(file, str):
            _, filename = os.path.split(file)
            if any(k in filename for k in ['left', 'lh']):
                hemisphere = 'left'
            elif any(k in filename for k in ['right', 'rh']):
                hemisphere = 'right'
            else:
                hemisphere = 'both'
            logger.warning("%s hemisphere(s) inferred from "
                           "filename" % hemisphere)
        # Get index :
        if hemisphere in ['left', 'lh']:
            idx = self.mesh._lr_index
        elif hemisphere in ['right', 'rh']:
            idx = ~self.mesh._lr_index
        else:
            idx = np.ones((len(self.mesh),), dtype=bool)
        return hemisphere, idx

    @staticmethod
    def _load_annot_file(file):
        """Load a .annot file."""
        assert os.path.isfile(file)
        is_nibabel_installed(raise_error=True)
        import nibabel
        # Get index and labels :
        id_vert, ctab, names = nibabel.freesurfer.read_annot(file)
        names = np.array(names).astype(str)
        color, u_idx = ctab[:, 0:4], ctab[..., -1]
        logger.info("    Annot file loaded (%s)" % file)
        # Test if variables have the same size :
        if len(u_idx) != len(names):
            min_len = min(len(u_idx), color.shape[0], len(names))
            logger.warning("Length of label names (%i) and index (%i) doesn't "
                           "match. Following label index ignored : %s" % (
                               len(names), len(u_idx),
                               ", ".join(u_idx[min_len::].astype(str))))
            color = color[0:min_len, :]
            names = names[0:min_len]
            u_idx = u_idx[0:min_len]
        return id_vert, color, names, u_idx

    ###########################################################################
    ###########################################################################
    #                               CBAR
    ###########################################################################
    ###########################################################################

    def _update_cbar(self):
        self.mesh.update_colormap(**self.to_kwargs())

    def _update_cbar_minmax(self):
        self._clim = self.mesh.minmax

    ###########################################################################
    ###########################################################################
    #                               PROPERTIES
    ###########################################################################
    ###########################################################################

    def __hemisphere_correction(self, arr, indexed_faces=False):
        mesh, hemi = self.mesh, self.mesh.hemisphere
        if hemi == 'both':
            return arr
        elif hemi in ['left', 'right']:
            lr = mesh._lr_index if hemi == 'left' else ~mesh._lr_index
            lr = mesh._lr_index[mesh._faces[:, 0]] if indexed_faces else lr
            return arr[lr, ...]

    # ----------- VERTICES -----------
    @property
    def vertices(self):
        """Get the vertices value."""
        return self.__hemisphere_correction(self.mesh._vertices)

    # ----------- FACES -----------
    @property
    def faces(self):
        """Get the faces value."""
        return self.__hemisphere_correction(self.mesh._faces, True)

    # ----------- NORMALS -----------
    @property
    def normals(self):
        """Get the normals value."""
        return self.__hemisphere_correction(self.mesh._normals)

    # ----------- HEMISPHERE -----------
    @property
    def hemisphere(self):
        """Get the hemisphere value."""
        return self.mesh.hemisphere

    @hemisphere.setter
    def hemisphere(self, value):
        """Set hemisphere value."""
        self.mesh.hemisphere = value

    # ----------- TRANSLUCENT -----------
    @property
    def translucent(self):
        """Get the translucent value."""
        return self.mesh.translucent

    @translucent.setter
    def translucent(self, value):
        """Set translucent value."""
        assert isinstance(value, bool)
        self.mesh.translucent = value

    # ----------- ALPHA -----------
    @property
    def alpha(self):
        """Get the alpha value."""
        return self.mesh.alpha

    @alpha.setter
    def alpha(self, value):
        """Set alpha value."""
        self.mesh.alpha = value

    # ----------- CAMERA -----------
    @property
    def camera(self):
        """Get the camera value."""
        return self.mesh._camera

    @camera.setter
    def camera(self, value):
        """Set camera value."""
        self.mesh.set_camera(value)
        self.reset_camera()

    # ----------- SCALE -----------
    @property
    def scale(self):
        """Get the scale value."""
        return self._scale

    @scale.setter
    def scale(self, value):
        """Set scale value."""
        self._scale = value
