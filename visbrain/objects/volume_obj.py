"""Volume object."""
import os
import numpy as np
import logging

from vispy import scene
from vispy.scene import visuals
from vispy.color import BaseColormap
from vispy.visuals.transforms import MatrixTransform

from .visbrain_obj import VisbrainObject, CombineObjects
from ..utils import (load_predefined_roi, wrap_properties, normalize,
                     array_to_stt, stt_to_array)
from ..io import (read_nifti, get_files_in_data, get_files_in_folders,
                  path_to_visbrain_data, get_data_path, path_to_tmp,
                  save_volume_template, remove_volume_template)


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

    def __call__(self, name, vol=None, hdr=None, labels=None, index=None,
                 system=None):
        """Load a predefined volume."""
        _, ext = os.path.splitext(name)
        if ('.nii' in ext) or ('gz' in ext):
            vol, _, hdr = read_nifti(name)
            name = os.path.split(name)[1].split('.nii')[0]
            self._name = name
            logger.info('Loading %s' % name)
            labels = index = system = None
        elif isinstance(name, str):
            path = self.list(file=name + '.npz')
            if len(path):
                self._name = os.path.split(path[0])[1].split('.npz')[0]
                logger.debug("%s volume loaded" % name)
                vol, labels, index, hdr, system = load_predefined_roi(path[0])

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

    def _search_in_path(self):
        """Specify where to find volume templates."""
        _vb_data = path_to_visbrain_data(folder='roi')
        _data = get_data_path(folder='roi')
        _tmp = path_to_tmp(folder='roi')
        return _vb_data, _data, _tmp

    def list(self, file=None):
        """Get the list of installed volumes."""
        return get_files_in_folders(*self._search_in_path(), file=file)

    def slice_to_pos(self, sl, axis=None):
        """Return the position from slice in the volume space."""
        single_val = isinstance(axis, int) and isinstance(sl, int)
        if single_val:
            val = sl
            sl = [0.] * 3
            sl[axis] = val
        assert len(sl) == 3 and isinstance(self._hdr, MatrixTransform)
        pos = self._hdr.map(sl)[0:-1]
        return pos[axis] if single_val else pos

    def pos_to_slice(self, pos, axis=None):
        """Return the slice from position."""
        single_val = isinstance(axis, int) and isinstance(pos, int)
        if single_val:
            val = pos
            pos = [0.] * 3
            pos[axis] = val
        assert len(pos) == 3 and isinstance(self._hdr, MatrixTransform)
        sl = np.round(self._hdr.imap(pos)).astype(int)[0:-1]
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
        if value in get_files_in_data('roi', with_ext=False):
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
        return get_files_in_folders(*_Volume._search_in_path(self), file=file)

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
    cmap : {'Opaquegrays', 'TransFire', 'OpaqueFire', 'TransGrays'}
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
