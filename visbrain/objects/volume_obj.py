"""Volume object."""
import os
import numpy as np
import logging

from vispy import scene
from vispy.scene import visuals
from vispy.color import BaseColormap
from vispy.visuals.transforms import MatrixTransform

from .visbrain_obj import VisbrainObject, CombineObjects
from ..utils import (wrap_properties, normalize, array_to_stt, stt_to_array)
from ..io import (read_nifti, save_volume_template, remove_volume_template,
                  download_file, path_to_visbrain_data, read_mist)


logger = logging.getLogger('visbrain')


class TransFire(BaseColormap):
    """Transparent fire colormap."""

    glsl_map = """
    vec4 translucent_fire(float t) {
        return vec4(pow(t, 0.5), t, t*t, t*0.05);
    }
    """


class OpaqueFire(BaseColormap):
    """Opaque fire colormap."""

    glsl_map = """
    vec4 translucent_fire(float t) {
        return vec4(pow(t, 0.5), t, t*t, max(0, t*1.05 - 0.05));
    }
    """


class TransGrays(BaseColormap):
    """Transparent gray colormap."""

    glsl_map = """
    vec4 translucent_grays(float t) {
        return vec4(t*t, t*t, t*t, t*0.05);
    }
    """


class OpaqueGrays(BaseColormap):
    """Opaque gray colormap."""

    glsl_map = """
    vec4 translucent_grays(float t) {
        return vec4(t*t, t*t, t*t, max(0, t*1.05 - 0.05));
    }
    """


VOLUME_CMAPS = {'TransFire': TransFire(), 'OpaqueFire': OpaqueFire(),
                'TransGrays': TransGrays(), 'OpaqueGrays': OpaqueGrays()}
KNOWN_METHODS = ['mip', 'translucent', 'additive', 'iso']


class _Volume(VisbrainObject):
    """Manage loaded volumes.

    This class is shared by volume classes (VolumeObj, RoiObj, CrossSecObj).
    """

    def __init__(self, name, parent, transform, verbose, **kw):
        """Init."""
        VisbrainObject.__init__(self, name, parent, transform, verbose, **kw)
        self.data_folder = 'roi'

    def __call__(self, name, vol=None, hdr=None, labels=None, index=None,
                 system=None):
        """Load a predefined volume."""
        _, ext = os.path.splitext(name)
        if ('.nii' in ext) or ('gz' in ext) or ('img' in ext):
            vol, _, hdr = read_nifti(name)
            name = os.path.split(name)[1].split('.nii')[0]
            self._name = name
            logger.info('    %s volume loaded' % name)
            labels = index = system = None
        elif isinstance(name, str):
            # Switch between MIST and {aal, brodmann...} :
            if 'MIST' in name.upper():
                mist_path = path_to_visbrain_data('mist', 'roi')
                if not os.path.isdir(mist_path):
                    download_file('mist.zip', astype='roi', unzip=True)
                (vol, labels, index, hdr), system = read_mist(name), 'mni'
            else:
                to_load, name_npz = None, name + '.npz'
                if name in self._df_get_downloaded():
                    to_load = self._df_get_file(name_npz, download=False)
                elif name_npz in self._df_get_downloadable():
                    to_load = self._df_download_file(name_npz)
                # Load file :
                if isinstance(to_load, str):
                    self._name = os.path.split(to_load)[1].split('.npz')[0]
                    arch = np.load(to_load)
                    vol, hdr = arch['vol'], arch['hdr']
                    labels, index = arch['labels'], arch['index']
                    system = 'tal' if 'talairach' in to_load else 'mni'
                    logger.debug("%s volume loaded" % name)
            self._name = name

        self._vol, self._hdr = self._check_volume(vol, hdr)
        self._labels, self._index, self._system = labels, index, system
        self._sh = vol.shape

    def save(self, tmpfile=False):
        """Save the volume template."""
        hdr = self._stt_to_array(self._hdr)
        save_volume_template(self.name, vol=self._vol, labels=self._labels,
                             index=self._index, hdr=hdr, tmpfile=tmpfile)

    def remove(self):
        """Remove the volume template."""
        remove_volume_template(self.name)

    def list(self, file=None):
        """Get the list of installed volumes."""
        return self._df_get_downloaded(file=file)

    def slice_to_pos(self, sl, axis=None, hdr=None):
        """Return the position from slice in the volume space."""
        single_val = isinstance(axis, int) and isinstance(sl, int)
        if single_val:
            val = sl
            sl = [0.] * 3
            sl[axis] = val
        if hdr is None:
            hdr = self._hdr
        assert len(sl) == 3 and isinstance(hdr, MatrixTransform)
        pos = hdr.map(sl)[0:-1]
        return pos[axis] if single_val else pos

    def pos_to_slice(self, pos, axis=None, hdr=None):
        """Return the slice from position."""
        single_val = isinstance(axis, int) and isinstance(pos, int)
        if single_val:
            val = pos
            pos = [0.] * 3
            pos[axis] = val
        if hdr is None:
            hdr = self._hdr
        assert len(pos) == 3 and isinstance(hdr, MatrixTransform)
        sl = np.round(hdr.imap(pos)).astype(int)[0:-1]
        return sl[axis] if single_val else sl

    @staticmethod
    def _array_to_stt(hdr):
        """Convert an hdr to MatrixTransform."""
        return array_to_stt(hdr)

    @staticmethod
    def _stt_to_array(arr):
        """Convert a MatrixTransform to hdr."""
        return stt_to_array(arr)

    @staticmethod
    def _check_volume(vol, hdr):
        assert vol.ndim == 3
        if hdr is None:
            hdr = np.eye(4)
        if isinstance(hdr, np.ndarray):
            hdr = array_to_stt(hdr)
        assert isinstance(hdr, MatrixTransform)
        return vol, hdr

    # ----------- NAME -----------
    @property
    def name(self):
        """Get the name value."""
        return self._name

    @name.setter
    def name(self, value):
        """Set name value."""
        if value in self.list():
            self(value)
            self.update()
            self._name = value


class _CombineVolume(CombineObjects):
    """Combine Volume objects."""

    def __init__(self, vol_type, objs=None, select=None, parent=None):
        """Init."""
        CombineObjects.__init__(self, vol_type, objs, select, parent)

    def list(self, file=None):
        """Get the list of installed volumes."""
        return self._df_get_downloaded(file=file)

    def save(self, tmpfile=False):
        for k in self:
            if k.name not in k.list():
                k.save(tmpfile=tmpfile)


class VolumeObj(_Volume):
    """Create a 3-D volume object.

    Parameters
    ----------
    name : string
        Name of the volume object. If name is 'brodmann', 'aal' or 'talairach'
        a predefined volume object is used and vol, index and label are
        ignored. The name input can also be the path to an nii.gz file.
    vol : array_like
        The volume to use. Should be a 3-d array.
    hdr : array_like | None
        Matrix transformation to apply. hdr should be a (4, 4) array.
    method : {'mip', 'translucent', 'additive', 'iso'}
        Volume rendering method. Default is 'mip'.
    threshold : float | 0.
        Threshold value for iso rendering method.
    cmap : {'OpaqueGrays', 'TransFire', 'OpaqueFire', 'TransGrays'}
        Colormap to use.
    select : list | None
        Select some structures in the volume.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Volume object parent.
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
    >>> from visbrain.objects import VolumeObj
    >>> select = [4, 6]  # select Brodmann area 4 and 6
    >>> v = VolumeObj('brodmann', method='iso', select=select)
    >>> v.preview(axis=True)
    """

    def __init__(self, name, vol=None, hdr=None, method='mip', threshold=0.,
                 cmap='OpaqueGrays', select=None, transform=None, parent=None,
                 preload=True, verbose=None, **kw):
        """Init."""
        _Volume.__init__(self, name, parent, transform, verbose, **kw)

        # _______________________ CHECKING _______________________
        # Create 3-D volume :
        vol_d = np.zeros((1, 1, 1), dtype=np.float32)
        self._vol3d = visuals.Volume(vol_d, parent=self._node,
                                     threshold=threshold, name='3-D Volume',
                                     cmap=VOLUME_CMAPS[cmap])
        if preload:
            self(name, vol, hdr, threshold, cmap, method, select)

    def __call__(self, name, vol=None, hdr=None, threshold=None, cmap=None,
                 method=None, select=None):
        """Change the volume."""
        _Volume.__call__(self, name, vol=vol, hdr=hdr)
        self.set_data(self._vol, hdr=self._hdr, threshold=threshold, cmap=cmap,
                      method=method, select=select)

    def set_data(self, vol, hdr=None, threshold=None, cmap=None,
                 method=None, select=None):
        """Set data to the volume."""
        if isinstance(select, (list, tuple)):
            logger.info("Extract structures %r from the volume" % select)
            st = '(vol != %s) & '.join([''] * (len(select) + 1))[0:-3]
            vol[eval(st % tuple(select))] = 0.
            threshold = 0.
        self._max_vol = vol.max()
        vol = normalize(vol)
        self._vol3d.set_data(np.transpose(vol, (2, 1, 0)))
        self._vol3d.transform = hdr
        self.method = method
        self.threshold = threshold
        self.cmap = cmap

    def extract_activity(self, xyz, radius=2.):
        """Extract activity of a volume around (x, y, z) points.

        Parameters
        ----------
        xyz : array_like
            Array of (x, y, z) coordinates of shape (n_sources, 3)
        radius : float | 2.
            Radius of the sphere around each point.

        Returns
        -------
        act : array_like
            Activity array of shape (n_sources,)
        """
        assert isinstance(xyz, np.ndarray) and (xyz.shape[1] == 3)
        assert isinstance(radius, (int, float))
        n_s = xyz.shape[0]
        # hdr conversion :
        logger.info("    Convert coordinates in volume space")
        hdr = self._hdr
        center, extrem = np.array([[0.] * 3]), np.array([[radius] * 3])
        xyz_m = np.round(hdr.imap(xyz)[:, 0:-1]).astype(int)
        radius_0 = np.round(hdr.imap(center)[:, 0:-1]).astype(int)
        radius_1 = np.round(hdr.imap(extrem)[:, 0:-1]).astype(int)
        rd = [max(int(k / 2), 1) for k in np.abs(radius_1 - radius_0).ravel()]
        # Extact activity :
        logger.info("    Extract activity of the %i sources defined" % n_s)
        act = np.zeros((n_s,), dtype=np.float32)
        for i, k in enumerate(xyz_m):
            act[i] = self._vol[k[0] - rd[0]:k[0] + rd[0],
                               k[1] - rd[1]:k[1] + rd[1],
                               k[2] - rd[2]:k[2] + rd[2]].mean()
        return act

    def update(self):
        """Update the volume."""
        self._vol3d.update()

    def _get_camera(self):
        """Get the most adapted camera."""
        sh = self._vol3d._vol_shape
        dist = np.linalg.norm(self._vol3d.transform.map(sh)[0:-1])
        cam = scene.cameras.TurntableCamera(scale_factor=dist, azimuth=0.,
                                            elevation=90.)
        cam.set_default_state()
        return cam

    ###########################################################################
    ###########################################################################
    #                             PROPERTIES
    ###########################################################################
    ###########################################################################

    # ----------- METHOD -----------
    @property
    def method(self):
        """Get the method value."""
        return self._method

    @method.setter
    @wrap_properties
    def method(self, value):
        """Set method value."""
        assert value in KNOWN_METHODS
        self._vol3d.method = value
        self.update()
        self._method = value

    # ----------- CMAP -----------
    @property
    def cmap(self):
        """Get the cmap value."""
        return self._cmap

    @cmap.setter
    @wrap_properties
    def cmap(self, value):
        """Set cmap value."""
        assert value in list(VOLUME_CMAPS.keys())
        self._vol3d.cmap = VOLUME_CMAPS[value]
        self.update()
        self._cmap = value

    # ----------- THRESHOLD -----------
    @property
    def threshold(self):
        """Get the threshold value."""
        return self._threshold

    @threshold.setter
    @wrap_properties
    def threshold(self, value):
        """Set threshold value."""
        assert isinstance(value, (int, float))
        if self.method == 'iso':
            self._vol3d.shared_program['u_threshold'] = value
            self.update()
            self._threshold = value

    # # ----------- ALPHA -----------
    # @property
    # def alpha(self):
    #     """Get the alpha value."""
    #     return self._alpha

    # @alpha.setter
    # @wrap_properties
    # def alpha(self, value):
    #     """Set alpha value."""
    #     assert isinstance(value, (int, float)) and (0. <= value <= 1.)
    #     self._vol3d.opacity = value
    #     self._alpha = value
