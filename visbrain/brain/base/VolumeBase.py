"""Oki."""
import numpy as np
import os
import sys

from vispy import scene
import vispy.visuals.transforms as vist
import vispy.scene.visuals as visu
from vispy.color import BaseColormap

from .CrossSecBase import CrossSections
from .RoiBase import RoiBase
from ...utils import array_to_stt, normalize

__all__ = ('VolumeBase')


class TransFire(BaseColormap):
    glsl_map = """
    vec4 translucent_fire(float t) {
        return vec4(pow(t, 0.5), t, t*t, t*0.05);
    }
    """


class OpaqueFire(BaseColormap):
    glsl_map = """
    vec4 translucent_fire(float t) {
        return vec4(pow(t, 0.5), t, t*t, max(0, t*1.05 - 0.05));
    }
    """


class TransGrays(BaseColormap):
    glsl_map = """
    vec4 translucent_grays(float t) {
        return vec4(t*t, t*t, t*t, t*0.05);
    }
    """


class OpaqueGrays(BaseColormap):
    glsl_map = """
    vec4 translucent_grays(float t) {
        return vec4(t*t, t*t, t*t, max(0, t*1.05 - 0.05));
    }
    """


class Volume3D(object):
    """Base class for 3-D volume.

    Parameters
    ----------
    parent : VisPy | None
        The VisPy parent.
    cmap : string | 'TransGrays'
        Colormap name.
    """

    def __init__(self, parent=None, cmap='OpaqueGrays'):
        """Init."""
        # Create the node for the 3-D volume :
        self._node_vol = scene.Node(name='Volume3D')
        self._node_vol.parent = parent
        # Colormaps :
        self._cmap_vol = cmap
        self._cmaps = {}
        self._cmaps['TransFire'] = TransFire()
        self._cmaps['OpaqueFire'] = OpaqueFire()
        self._cmaps['TransGrays'] = TransGrays()
        self._cmaps['OpaqueGrays'] = OpaqueGrays()
        # Create 3-D volume :
        vol = np.zeros((1, 1, 1), dtype=np.float32)
        self.vol3d = visu.Volume(vol, parent=self._node_vol, threshold=0.,
                                 cmap=self._cmaps[cmap])

    def set_vol_data(self, method='mip', update=True, cmap='OpaqueGrays',
                     threshold=0.):
        """Set volume data.

        Parameters
        ----------
        method : {'mip', 'translucent', 'additive', 'iso'}
            Volume rendering method.
        update : bool | True
            Specify if volume data has to be updated.
        cmap : string | 'TransGrays'
            Colormap name.
        """
        # Update bol :
        if update or (self.vol3d._vol_shape == (1, 1, 1)):
            vol = self.vol.copy()
            vol = normalize(vol)
            self.vol3d.set_data(np.transpose(vol, (2, 1, 0)))
        if method in ['mip', 'translucent', 'additive', 'iso']:
            self.vol3d.method = method
        if method == 'iso':
            self.vol3d.threshold = threshold
        if cmap is not self._cmap_vol:
            self.vol3d.cmap = self._cmaps[cmap]
            self._cmap_vol = cmap

    # ----------- VISIBLE_VOL -----------
    @property
    def visible_vol(self):
        """Get the visible_vol value."""
        return self._visible_vol

    @visible_vol.setter
    def visible_vol(self, value):
        """Set visible_vol value."""
        self._visible_vol = value
        self._node_vol.visible = value


class VolumeObject(object):
    """Create a basic volume object.

    Parameters
    ----------
    name : string
        Name of the volume to use.
    vol : array_like
        The volume to use for cross-sections of shape (nx, ny, nz).
    transform : VisPy.tranformation | None
        The associated transformation. Should be a MatrixTransform.
    roi_values : array_like | None
        Array of unique index.
    roi_labels : array_like | None
        Array of labels in the same order as roi_values.
    """

    def __init__(self, name, vol, transform=None, roi_values=None,
                 roi_labels=None):
        """Init."""
        #######################################################################
        #                               CHECK DATA
        #######################################################################
        # Name :
        if isinstance(name, str):
            self.name = name
        else:
            raise ValueError("The name variable must be a string.")
        # Volume :
        if isinstance(vol, np.ndarray) and (vol.ndim == 3):
            self.vol = vol
        else:
            raise ValueError("The vol variable must be 3-D array.")
        # Transformation :
        if not isinstance(transform, vist.MatrixTransform):
            self.transform = vist.MatrixTransform()
        else:
            self.transform = transform
        # Index and label :
        if isinstance(roi_values, np.ndarray) and isinstance(
                roi_labels, np.ndarray):
            self._is_roi = len(roi_labels) == len(roi_values)
        else:
            self._is_roi = False
        self.roi_values = roi_values
        self.roi_labels = roi_labels
        # Get (nx, ny, nz) and minmax :
        self._sh = vol.shape
        self._nx, self._ny, self._nz = np.array(self._sh) - 1
        self._minmax = (vol.min(), vol.max())
        self._clim = self._minmax

    def get(self):
        kwargs = {}
        kwargs['transform'] = self.transform
        kwargs['roi_values'] = self.roi_values
        kwargs['roi_labels'] = self.roi_labels
        return (self.name, self.vol), kwargs


class VolumeBase(CrossSections, Volume3D, RoiBase):
    """Base class for volumes.

    This class is responsible for managing three types of objects :
        * Cross-sections : intersection of three images.
        * ROI : region of interest.
        * Volume : volume representation.

    Those objects shared loaded volumes.
    """

    def __init__(self, parent_sp):
        """Init."""
        self._vols = {}

        # Create a volume root node :
        self._node = scene.Node(name='Volume')

        # Initialize Cross-Sections, ROI and volume :
        Volume3D.__init__(self, parent=self._node)
        CrossSections.__init__(self, parent=self._node, parent_sp=parent_sp)
        RoiBase.__init__(self, parent=self._node)

        # Load default templates and select Brodmann:
        self._load_default()
        self.select_volume('Brodmann')

    def __bool__(self):
        """Return if defaults Brodmann and AAL are already loaded."""
        is_aal = 'AAL' in self._vols.keys()
        is_brod = 'Brodmann' in self._vols.keys()
        return is_aal or is_brod

    def __getitem__(self, name):
        """Get the volume referenced as name."""
        return self._vols[name]

    def _load_default(self):
        """Load the AAL and Brodmann atlas."""
        # _______________ LOAD _______________
        # Get path to the roi.npz file :
        cur_path = sys.modules[__name__].__file__.split('Volume')[0]
        roi_path = (cur_path, 'templates', 'roi.npz')
        path = os.path.join(*roi_path)
        # Load the volume :
        v = np.load(path)
        # Define the transformation :
        tr = array_to_stt(v['hdr'])

        # _______________ BRODMANN _______________
        # Add Brodmann volume :
        vol = v['brod_idx']
        roi_values = np.unique(vol)[1::]
        # label = np.array(["%.2d" % k + ': BA' + str(k) for num, k
        #                   in enumerate(roi_values)])
        label = self._labels_to_gui(roi_values.astype(str), 'BA')
        # Add Brodmann to referenced volumes :
        self.add_volume('Brodmann', vol, transform=tr, roi_values=roi_values,
                        roi_labels=label)

        # _______________ AAL _______________
        # Add AAL volume :
        vol = v['vol']
        roi_values = np.unique(v['aal_idx'])
        nlabel = len(v['aal_label'])
        # Get labels for left / right hemispheres :
        l, r = np.full((nlabel,), ' (L)'), np.full((nlabel,), ' (R)')
        label_l = np.core.defchararray.add(v['aal_label'], l)
        label_r = np.core.defchararray.add(v['aal_label'], r)
        label = self._labels_to_gui(np.c_[label_l, label_r].flatten())
        # Add AAL to referenced volumes :
        self.add_volume('AAL', vol, transform=tr, roi_values=roi_values,
                        roi_labels=label)

    def add_volume(self, name, vol, **kwargs):
        """Add a new volume.

        Parameters
        ----------
        name : string
            Name of the volume to add.
        vol : array_like
            The volume to use for cross-sections of shape (nx, ny, nz).
        kwargs : dict | {}
            Further arguments are passed to the VolumeObject.
        """
        self._vols[name] = VolumeObject(name, vol, **kwargs)

    def select_volume(self, name):
        """Select a volume.

        Parameters
        ----------
        name : string
            Name of the volume to use.
        """
        # Get the volume arguments :
        args, kwargs = self._vols[name].get()
        # Select this volume :
        VolumeObject.__init__(self, *args, **kwargs)
        # Set the associated transformation :
        self._node.transform = self.transform
        self._node.update()

    def update(self):
        """Update nodes."""
        self._node.update()
        self._node_vol.update()
        self._node_cs.update()

    def _labels_to_gui(self, label, pattern=''):
        """Convert list of labels for GUI integration.

        Convert "label" => "00: " + pattern + "label"

        Parameters
        ----------
        label : array_like
            Array of labels.
        pattern : string | ''
            Pattern to add to each label.

        Returns
        -------
        roi_labels : array_like
            Array of labels to be integrated into the GUI.
        """
        n_labels = len(label)
        n_digit = "%." + str(len(str(n_labels))) + "d"
        roi_labels = [n_digit % k + ": " + pattern + i for k, i
                      in enumerate(label)]
        return np.array(roi_labels)

    # ----------- PARENT -----------
    @property
    def parent(self):
        """Get the parent value."""
        return self._parent

    @parent.setter
    def parent(self, value):
        """Set parent value."""
        self._parent = value
        self._node.parent = value
