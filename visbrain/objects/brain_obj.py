"""Base class for objects of type brain."""
import os
import numpy as np
import logging

from vispy import scene

from .visbrain_obj import VisbrainObject
from ..visuals import BrainMesh
from ..utils import get_data_path, mesh_edges, smoothing_matrix, array2colormap
from ..io import download_file

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
                 transform=None, parent=None, verbose=None):
        """Init."""
        # Init Visbrain object base class :
        VisbrainObject.__init__(self, name, parent, transform, verbose)
        # Load brain template :
        self._scale = 1.
        self.set_data(name, vertices, faces, normals, lr_index, hemisphere)
        self.translucent = translucent

    def __len__(self):
        """Get the number of vertices."""
        return self.vertices.shape[0]

    def set_data(self, name=None, vertices=None, faces=None, normals=None,
                 lr_index=None, hemisphere='both'):
        """Load a brain template."""
        # _______________________ DEFAULT _______________________
        b_download = self._get_downloadable_templates()
        b_installed = self._get_installed_templates()
        # Need to download the brain template :
        if (name in b_download) and (name not in b_installed):
            self._add_downloadable_templates(name)
        if name in self._get_installed_templates():  # predefined
            (vertices, faces, normals,
             lr_index) = self._load_brain_template(name)

        # _______________________ CHECKING _______________________
        assert all([isinstance(k, np.ndarray) for k in (vertices, faces)])
        if normals is not None:  # vertex normals
            assert isinstance(normals, np.ndarray)
        assert (lr_index is None) or isinstance(lr_index, np.ndarray)
        assert hemisphere in ['both', 'left', 'right']

        self._define_mesh(vertices, faces, normals, lr_index, hemisphere)

    def _define_mesh(self, vertices, faces, normals, lr_index, hemisphere):
        """Define brain mesh."""
        if not hasattr(self, 'mesh'):
            # Mesh brain :
            self.mesh = BrainMesh(vertices=vertices, faces=faces,
                                  normals=normals, lr_index=lr_index,
                                  hemisphere=hemisphere, parent=self._node,
                                  name='Mesh')
        else:
            self.mesh.set_data(vertices=vertices, faces=faces, normals=normals,
                               lr_index=lr_index, hemisphere=hemisphere)

    def _load_brain_template(self, name, path=None):
        """Load the brain template.

        If path is None, use the default visbrain/data folder.
        """
        if path is None:
            name = os.path.join(self._get_template_path(), name + '.npz')
        arch = np.load(name)
        vertices, faces = arch['vertices'], arch['faces']
        normals = arch['normals']
        lr_index = arch['lr_index'] if 'lr_index' in arch.keys() else None
        return vertices, faces, normals, lr_index

    ###########################################################################
    ###########################################################################
    #                           PATH METHODS
    ###########################################################################
    ###########################################################################

    def _get_template_path(self):
        """Get the path where datasets are stored."""
        return get_data_path(folder='templates')

    def _get_all_available_templates(self):
        """Get all available brain templates (e.g defaults and downloadable."""
        b_def = self._get_default_templates()
        b_down = self._get_downloadable_templates()
        b_installed = self._get_installed_templates()
        b_all = list(set(b_def + b_down + b_installed))
        b_all.sort()
        return b_all

    def _get_default_templates(self):
        """Get the default list of brain templates."""
        return ['B1', 'B2', 'B3']

    def _get_downloadable_templates(self):
        """Get the list of brain that can be downloaded."""
        logger.debug("hdr transformation missing for downloadable templates")
        return ['white', 'inflated', 'sphere']

    def _get_installed_templates(self):
        """Get the list of available brain templates."""
        all_files = os.listdir(self._get_template_path())
        surf_list = [os.path.splitext(k)[0] for k in all_files]
        surf_list.sort()
        return surf_list

    def _add_downloadable_templates(self, name):
        """Download then install a brain template."""
        assert name in self._get_downloadable_templates()
        to_path = self._get_template_path()
        # Download the file :
        download_file(name + '.npz', to_path=to_path)

    ###########################################################################
    ###########################################################################
    #                           CAMERA // ROTATION
    ###########################################################################
    ###########################################################################

    def _get_camera(self):
        """Get the most adapted camera."""
        if self.mesh._camera is None:
            camera = scene.cameras.TurntableCamera(name='turntable')
            self.mesh.set_camera(camera)
            self.reset_camera()
        return self.camera

    def _optimal_camera_properties(self, with_distance=True):
        """Get the optimal camera properties."""
        center = self.mesh._center * self._scale
        sc = 1.08 * self.mesh._camratio[-1]
        prop = {'center': center, 'scale_factor': sc, 'azimuth': 0.,
                'elevation': 90, 'distance': 4 * sc}
        if with_distance:
            return prop
        else:
            del prop['distance']
            return prop

    def reset_camera(self):
        """Reset the camera."""
        cam_args = self._optimal_camera_properties()
        self.mesh._camera.distance = cam_args['distance']
        del cam_args['distance']
        self.mesh._camera.set_state(cam_args)
        self.mesh._camera.set_default_state()

    def set_state(self, azimuth=None, elevation=None, scale_factor=None,
                  distance=None, center=None, margin=1.08):
        """Set the camera state."""
        distance = scale_factor * 4.
        if isinstance(azimuth, (int, float)):
            self.mesh._camera.azimuth = azimuth
        if isinstance(elevation, (int, float)):
            self.mesh._camera.elevation = elevation
        if isinstance(scale_factor, (int, float)):
            self.mesh._camera.scale_factor = margin * scale_factor * self.scale
        if isinstance(distance, (int, float)):
            self.mesh._camera.distance = distance * self.scale
        if (center is not None) and len(center) == 3:
            self.mesh._camera.center = center
        self.mesh._camera.update()

    def rotate(self, fixed='top', custom=None, margin=.08):
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
        scale_factor = None
        if fixed in ['sagittal_0', 'left']:     # left
            azimuth, elevation = -90, 0
            scale_factor = self.mesh._camratio[-1]
        elif fixed in ['sagittal_1', 'right']:  # right
            azimuth, elevation = 90, 0
            scale_factor = self.mesh._camratio[-1]
        elif fixed in ['coronal_0', 'front']:   # front
            azimuth, elevation = 180, 0
            scale_factor = self.mesh._camratio[-1]
        elif fixed in ['coronal_1', 'back']:    # back
            azimuth, elevation = 0, 0
            scale_factor = self.mesh._camratio[-1]
        elif fixed in ['axial_0', 'top']:       # top
            azimuth, elevation = 0, 90
            scale_factor = self.mesh._camratio[1]
        elif fixed in ['axial_1', 'bottom']:    # bottom
            azimuth, elevation = 0, -90
            scale_factor = self.mesh._camratio[1]

        if isinstance(custom, (tuple, list)) and (len(custom) == 2):
            azimuth, elevation = tuple(custom)

        self.set_state(azimuth, elevation, scale_factor=scale_factor)

    def add_activation(self, data, vertices, smoothing_steps=20,
                       cmap='viridis', clim=None, vmin=None, vmax=None,
                       under='gray', over='red'):
        """Add activation to specific vertices.

        Parameters
        ----------
        data : array_like
            Vector array of data of shape (n_data,).
        vertices : array_like
            Vector array of vertices of shape (n_vtx). Must be an array of
            integers.
        smoothing_steps : int | 20
            Number of smoothing steps (smoothing is used if n_data < n_vtx)
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
        assert isinstance(data, np.ndarray) and (data.ndim == 1)
        assert isinstance(vertices, np.ndarray) and (vertices.ndim == 1)
        assert isinstance(smoothing_steps, int)
        # Get smoothed vertices // data :
        smooth_mat = smoothing_matrix(vertices, mesh_edges(self.mesh._faces),
                                      smoothing_steps=smoothing_steps)
        smooth_data = data[smooth_mat.col]
        # Fix clim :
        clim = (smooth_data.min(), smooth_data.max()) if clim is None else clim
        assert len(clim) == 2
        # Convert into colormap :
        smooth_map = array2colormap(smooth_data, cmap=cmap, clim=clim,
                                    vmin=vmin, vmax=vmax, under=under,
                                    over=over)
        color = np.ones((len(self.mesh), 4), dtype=np.float32)
        color[smooth_mat.row, :] = smooth_map
        # Set color to the mesh :
        self.mesh.color = color
        self.mesh.mask = smooth_mat.row[smooth_data >= clim[0]]

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
