"""Volume object."""
import numpy as np

from vispy import scene
from vispy.scene import visuals
from vispy.color import BaseColormap
# import vispy.visuals.transforms as vist

from .visbrain_obj import VisbrainObject
from ..utils import load_predefined_roi, array_to_stt


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


volume_cmaps = {'TransFire': TransFire(), 'OpaqueFire': OpaqueFire(),
                'TransGrays': TransGrays(), 'OpaqueGrays': OpaqueGrays()}


class VolumeBaseObject(object):
    """Base class for objects that use 3-D volumes.

    This class is inherited by :
        * VolumeObj : 3-D volume rendering object.
        * CrossSectionObj : cross-sections object.
        * RoiObj : region of interest object.
    """

    def __init__(self, name):
        """Init."""
        self._name = name

    def _predefined_volumes(self):
        """Get the list of predefined volumes."""
        return ['brodmann', 'aal', 'talairach']

    def _check_predefined_volume(self, name, vol, vol_type=True):
        if name in self._predefined_volumes():
            pass
            # args = load_predefined_roi(name)

    def _volume_update(self):
        raise NotImplementedError

    # ----------- NAME -----------
    @property
    def name(self):
        """Get the name value."""
        return self._name

    @name.setter
    def name(self, value):
        """Set name value."""
        assert isinstance(value, str)
        self._name = value
        if value in self._predefined_volumes():
            self._volume_update()


class VolumeObj(VolumeBaseObject, VisbrainObject):
    """Create a 3-D volume object.

    Parameters
    ----------
    name : string
        Name of the volume object. If name is 'brodmann', 'aal' or 'talairach'
        a predefined volume object is used and vol, index and label are
        ignored.
    method : {'mip', 'translucent', 'additive', 'iso'}
            Volume rendering method.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Volume object parent.
    """

    def __init__(self, name, vol=None, method='mip', threshold=0.,
                 cmap='OpaqueGrays', transform=None, parent=None):
        """Init."""
        VisbrainObject.__init__(self, name, parent, transform)
        VolumeBaseObject.__init__(self, name)

        # _______________________ CHECKING _______________________

        # Create 3-D volume :
        vol = np.zeros((1, 1, 1), dtype=np.float32)
        self._vol3d = visuals.Volume(vol, parent=self._node,
                                     threshold=threshold, name='3-D Volume',
                                     cmap=volume_cmaps[cmap])
        self.name = name

    def update(self):
        """Update the volume."""
        self._vol3d.update()

    def _get_camera(self):
        """Get the most adapted camera."""
        return scene.cameras.TurntableCamera()

    def _volume_update(self):
        """Update the volume."""
        vol, _, _, tr, _ = load_predefined_roi(self.name)
        assert isinstance(vol, np.ndarray) and (vol.ndim == 3)
        self._vol3d.set_data(vol)
        self._vol3d.transform = array_to_stt(tr)

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
    def method(self, value):
        """Set method value."""
        assert value in ['mip', 'translucent', 'additive', 'iso']
        self._vol3d.method = value()
        self.update()
        self._method = value

    # ----------- CMAP -----------
    @property
    def cmap(self):
        """Get the cmap value."""
        return self._cmap

    @cmap.setter
    def cmap(self, value):
        """Set cmap value."""
        assert value in list(volume_cmaps.keys())
        self._vol3d.cmap = volume_cmaps[value]
        self.update()
        self._cmap = value

    # ----------- ALPHA -----------
    @property
    def alpha(self):
        """Get the alpha value."""
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        """Set alpha value."""
        assert isinstance(value, (int, float)) and (0. <= value <= 1.)
        self._vol3d.opacity = value
        self._alpha = value

    # ----------- THRESHOLD -----------
    @property
    def threshold(self):
        """Get the threshold value."""
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        """Set threshold value."""
        assert isinstance(value, (int, float))
        self._vol3d.threshold = value
        self.update()
        self._threshold = value
