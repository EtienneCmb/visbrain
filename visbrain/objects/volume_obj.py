"""Volume object."""
import os
import numpy as np
import logging

from vispy import scene
from vispy.scene import visuals
from vispy.color import BaseColormap
from vispy.visuals.transforms import MatrixTransform

from .visbrain_obj import VisbrainObject
from ..utils import (load_predefined_roi, array_to_stt, wrap_properties,
                     normalize, get_files_in_data)
from ..io import read_nifti


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

    Use : _Volume('aal')
    """

    def __init__(self, name, vol, hdr, parent, transform, verbose, **kw):
        """Init."""
        # _______________________ NII.GZ _______________________
        _, ext = os.path.splitext(name)
        if name in get_files_in_data('roi', with_ext=False):
            print('NAME : ', name)
            vol, _, _, hdr, _ = self(name)
        elif ('.nii' in ext) or ('gz' in ext):
            vol, _, hdr = read_nifti(name)
            name = os.path.split(name)[1]
            logger.info('Loading %s' % name)

        VisbrainObject.__init__(self, name, parent, transform, verbose, **kw)

        return name, vol, hdr

    def __call__(self, name):
        """Load a predefined volume."""
        if name in get_files_in_data('roi', with_ext=False):
            logger.debug("%s volume loaded" % name)
            self._name = name
            return load_predefined_roi(name)
        else:
            logger.error("%s volume not in visbrain/data/roi/" % name)

    @staticmethod
    def slice_to_pos(hdr, sl, axis=None):
        """Return the position from slice in the volume space."""
        single_val = isinstance(axis, int) and isinstance(sl, int)
        if single_val:
            val = sl
            sl = [0.] * 3
            sl[axis] = val
        assert len(sl) == 3 and isinstance(hdr, MatrixTransform)
        pos = hdr.map(sl)[0:-1]
        return pos[axis] if single_val else pos

    @staticmethod
    def pos_to_slice(hdr, pos, axis=None):
        """Return the slice from position."""
        single_val = isinstance(axis, int) and isinstance(pos, int)
        if single_val:
            val = pos
            pos = [0.] * 3
            pos[axis] = val
        assert len(pos) == 3 and isinstance(hdr, MatrixTransform)
        sl = hdr.imap(pos).astype(int)[0:-1]
        return sl[axis] if single_val else sl

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
                 verbose=None, **kw):
        """Init."""
        name, vol, hdr = _Volume.__init__(self, name, vol, hdr, parent,
                                          transform, verbose, **kw)

        # _______________________ CHECKING _______________________
        # Create 3-D volume :
        vol_d = np.zeros((1, 1, 1), dtype=np.float32)
        self._vol3d = visuals.Volume(vol_d, parent=self._node,
                                     threshold=threshold, name='3-D Volume',
                                     cmap=VOLUME_CMAPS[cmap])
        self.set_data(name, vol, hdr, threshold, cmap, method, select)

    def set_data(self, name, vol=None, hdr=None, threshold=None, cmap=None,
                 method=None, select=None):
        """Set data to the volume."""
        vol, hdr = self._check_volume(vol, hdr)
        # assert isinstance(hdr, np.ndarray) and hdr.shape == (4, 4)
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
            self._vol3d.shared_program['u_threshold'] = value / self._max_vol
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