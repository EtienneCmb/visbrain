"""File for Cross-sections object."""
import numpy as np
import os
import sys

from vispy import scene
import vispy.scene.visuals as visu
import vispy.visuals.transforms as vist
from vispy.util.transforms import rotate

from ...utils import array2colormap, color2vb, CbarArgs, array_to_stt

__all__ = ('CrossSections')


class ImageSection(visu.Image):
    """Base class for one section image.

    Parameters
    ----------
    parent : VisPy | None
        VisPy parent.
    """

    def __init__(self, parent=None, interpolation='bilinear'):
        """Init."""
        visu.Image.__init__(self, parent=parent, interpolation=interpolation)
        self.unfreeze()
        self._zeros = 0.
        self._idx = 0
        self.freeze()

    def set_data(self, data, zeros, idx):
        """Set image data.

        Parameters
        ----------
        data : array_like
            Array of RGBBA color data of shape (n_rows, n_cols, 4).
        zeros : array_like
            Array of boolean values where the image is 0.
        idx : int
            Offset integer.
        """
        # Set data to visu.Image :
        super(visu.Image, self).set_data(data)
        # Keep the index and boolean index where the image is 0 :
        self._zeros = zeros
        self._idx = idx

    def set_color(self, bgcolor=None, alpha=None):
        """Set color and opacity for zeros values.

        Parameters
        ----------
        bgcolor : string/tuple | None
            Background color for zeros values.
        alpha : float | None
            Opacity for zeros values.
        """
        # Set color for zero values :
        if bgcolor is not None:
            self._data[self._zeros, 0:3] = bgcolor
        # Set opacity for zero values :
        if isinstance(alpha, (int, float)):
            self._data[self._zeros, 3] = alpha


class CrossSections(CbarArgs):
    """Cross-sections images based on a volume.

    Parameters
    ----------
    vol : array_like
        The volume to use for cross-sections of shape (nx, ny, nz).
    hdr : array_like
        Tranformation array of shape (4, 4). This array contains rotations and
        translations.
    parent : VisPy | None
        VisPy parent.
    visible : bool | True
        Set cross-sections visible.
    """

    def __init__(self, vol=None, hdr=None, parent=None, visible=True,
                 cmap='viridis'):
        """Init."""
        self._vol = vol
        self._hdr = hdr
        self._roi = {}
        self._visible = visible
        self._nx = (0, 100)
        self._ny = (0, 100)
        self._nz = (0, 100)
        self._transform = {}
        #######################################################################
        #                           TRANFORMATIONS
        #######################################################################
        # Translations :
        self._tr_coron = vist.STTransform()
        self._tr_sagit = vist.STTransform()
        self._tr_axial = vist.STTransform()
        # Rotations :
        rot_m90x = vist.MatrixTransform(rotate(-90, [1, 0, 0]))
        rot_180x = vist.MatrixTransform(rotate(180, [1, 0, 0]))
        rot_90y = vist.MatrixTransform(rotate(90, [0, 1, 0]))
        rot_m90y = vist.MatrixTransform(rotate(-90, [0, 1, 0]))
        rot_m180y = vist.MatrixTransform(rotate(-180, [0, 1, 0]))
        rot_90z = vist.MatrixTransform(rotate(90, [0, 0, 1]))
        # Tranformations :
        tf_sagit = [self._tr_sagit, rot_90z, rot_m90y, rot_m90x]
        tf_coron = [self._tr_coron, rot_90z, rot_180x, rot_90y]
        tf_axial = [self._tr_axial, rot_m180y, rot_90z]

        #######################################################################
        #                            ELEMENTS
        #######################################################################
        # Create a root node :
        self._node = scene.Node(name='ImInter')
        # Axial :
        self.axial = ImageSection(parent=self._node)
        self.axial.transform = vist.ChainTransform(tf_axial)
        # Coronal :
        self.coron = ImageSection(parent=self._node)
        self.coron.transform = vist.ChainTransform(tf_coron)
        # Sagittal :
        self.sagit = ImageSection(parent=self._node)
        self.sagit.transform = vist.ChainTransform(tf_sagit)

        self._node.transform = vist.MatrixTransform()
        self._node.parent = parent
        self._node.visible = visible

        kwargs = {'depth_test': True, 'cull_face': False, 'blend': False,
                  'blend_func': ('src_alpha', 'one_minus_src_alpha')}
        self.sagit.set_gl_state('translucent', **kwargs)
        self.coron.set_gl_state('translucent', **kwargs)
        self.axial.set_gl_state('translucent', **kwargs)

        CbarArgs.__init__(self, cmap, (0, 100), False, None, False, None,
                          None, None)

    def _check_data(self):
        """Check volume and data and tranformations.

        This method also load the ROI template if empty.
        """
        # Load volume if needed :
        if 'AAL' not in self._roi.keys():
            # Get path to the roi.npz file :
            cur_path = sys.modules[__name__].__file__.split('Cross')[0]
            roi_path = (cur_path, 'templates', 'roi.npz')
            path = os.path.join(*roi_path)
            # Load the volume :
            v = np.load(path)
            # Define the transformation :
            tr = array_to_stt(v['hdr'])
            # hdr = v['hdr'][0:-1, -1]
            # transform_aal = vist.STTransform(translate=hdr)
            # transform_brod = vist.STTransform(translate=hdr)
            # Add Brodmann volume :
            self.add_volume('Brodmann', v['brod_idx'], tr)
            self.add_volume('AAL', v['vol'], tr)
            # Set Brodmann as the default template to use :
            self.set_volume('Brodmann')

        # Check volume :
        if (self._vol.ndim != 3) or (self._vol.min() != 0):
            raise ValueError("The volume must be a 3-D array with values "
                             "starting from 0.")

    def set_data(self, dx=None, dy=None, dz=None, bgcolor=(.2, .2, .2),
                 alpha=0., cmap=None, update=False):
        """Set data to cross-sections.

        Parameters
        ----------
        dx : int | None
            Offset for the sagittal image.
        dy : int | None
            Offset for the coronale image.
        dz : int | None
            Offset for the axial image.
        bgcolor : string/tuple | None
            Background color for zeros values.
        alpha : float | None
            Opacity for zeros values.
        cmap : string | None
            Colormap name.
        update : bool | False
            Force updating.
        """
        # Get the colormap :
        if cmap is None:
            cmap = self._cmap
        else:
            self._cmap = cmap

        # Sagittal image :
        if (dx is not None) or update:
            if dx is None:
                dx = self.sagit._idx
            sagit = self._vol[dx, :, :]
            sagit_z = sagit == 0
            sagit_cmap = array2colormap(sagit, clim=self._clim, cmap=cmap)
            self.sagit.set_data(sagit_cmap, sagit_z, dx)

        # Coronal image :
        if (dy is not None) or update:
            if dy is None:
                dy = self.coron._idx
            coro = self._vol[:, dy, :]
            coro_z = coro == 0
            coro_cmap = array2colormap(coro, clim=self._clim, cmap=cmap)
            coro_cmap[dx - 1:dx + 1, :, 0:3] = 0.
            self.coron.set_data(coro_cmap, coro_z, dy)

        # Axial image :
        if (dz is not None) or update:
            if dz is None:
                dz = self.axial._idx
            axial = self._vol[:, :, dz]
            axial_z = axial == 0
            axial_cmap = array2colormap(axial, clim=self._clim, cmap=cmap)
            axial_cmap[dx - 1:dx + 1, :, 0:3] = 0.
            axial_cmap[:, dy - 1:dy + 1, 0:3] = 0.
            self.axial.set_data(axial_cmap, axial_z, dz)

        # Translate images to (dx, dy, dz) :
        if any([dx, dy, dz, update]):
            self._move_images(dx, dy, dz)

        # Set opacity level and color :
        if bgcolor is not None:
            bgcolor = color2vb(bgcolor)[:, 0:-1]
        if alpha is not None:
            self.sagit.set_color(bgcolor, alpha)
            self.coron.set_color(bgcolor, alpha)
            self.axial.set_color(bgcolor, alpha)

        self._node.update()

    def _move_images(self, dx=None, dy=None, dz=None):
        """Move images to a defined center.

        Parameters
        ----------
        dx : int | None
            Offset for the sagittal image.
        dy : int | None
            Offset for the coronale image.
        dz : int | None
            Offset for the axial image.
        """
        # Sagittal image :
        if dx is not None:
            tr = self._tr_sagit.translate
            self._tr_sagit.translate = (dx, tr[1], tr[2], tr[3])
        # Coronal image :
        if dy is not None:
            tr = self._tr_coron.translate
            self._tr_coron.translate = (tr[0], dy, tr[2], tr[3])
        # Axial image :
        if dz is not None:
            tr = self._tr_axial.translate
            self._tr_axial.translate = (tr[0], tr[1], dz, tr[3])

    def set_volume(self, name):
        """Set new volume data.

        Parameters
        ----------
        name : string
            Name of the volume to use.
        """
        # Set the volume and corresponding tranformation :
        self._vol = self._roi[name]
        self._node.transform = self._transform[name]
        # Get (min, max) across (x, y, z) axes :
        self._nx = (0, self._vol.shape[0] - 1)
        self._ny = (0, self._vol.shape[1] - 1)
        self._nz = (0, self._vol.shape[2] - 1)
        # Get fixed clim :
        self._clim = (self._vol.min(), self._vol.max())
        self._minmax = self._clim
        # self._node.transform.update()
        # self._node.update()

    def add_volume(self, name, vol, transform=None):
        """Add a new volume.

        Parameters
        ----------
        name : string
            Name of the volume to use.
        vol : array_like
            The volume to use for cross-sections of shape (nx, ny, nz).
        transform : VisPy.tranformation | None
            The associated transformation.
        """
        # Add volume and transformation :
        if transform is None:
            transform = vist.NullTransform()
        self._roi[name] = vol
        self._transform[name] = transform

    # ----------- VISIBLE -----------
    @property
    def visible(self):
        """Get the visible value."""
        return self._visible

    @visible.setter
    def visible(self, value):
        """Set visible value."""
        self._check_data()
        self._visible = value
        self._node.visible = value
