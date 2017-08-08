"""File for Cross-sections object."""
import numpy as np

from vispy import scene
import vispy.scene.visuals as visu
import vispy.visuals.transforms as vist
from vispy.util.transforms import rotate

from ...utils import array2colormap

__all__ = ('CrossSections')


class ImageSection(visu.Image):
    """Base class for one section image.

    Parameters
    ----------
    name : string | None
        Name of the image.
    parent : VisPy | None
        VisPy parent.
    interpolation : string | 'bilinear'
        Interpolation method to pass to the visu.Image object.
    """

    def __init__(self, name=None, parent=None, interpolation='bilinear'):
        """Init."""
        visu.Image.__init__(self, parent=parent, interpolation=interpolation,
                            name=name)
        self.unfreeze()
        self._zeros = 0.
        self._idx = 0
        self.freeze()

    def set_data(self, data, zeros, idx):
        """Set image data.

        Parameters
        ----------
        data : array_like
            Array of RGBA color data of shape (n_rows, n_cols, 4).
        zeros : array_like
            Array of boolean values where the image is 0.
        idx : int
            Offset integer.
        """
        # Keep data shape :
        self.unfreeze()
        self._sh = data[..., 0].shape
        self.freeze()
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


class CrossSections(object):
    """Cross-sections images based on a volume.

    Parameters
    ----------
    parent : VisPy | None
        VisPy parent.
    visible : bool | True
        Set cross-sections visible.
    """

    def __init__(self, parent=None, visible=True, cmap='viridis'):
        """Init."""
        self._visible_cs = visible
        self._cmap_cs = cmap
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
        self._node_cs = scene.Node(name='Cross-Sections')
        self._node_cs.parent = parent
        self._node_cs.visible = visible
        # Axial :
        self.axial = ImageSection(parent=self._node_cs, name='Axial')
        self.axial.transform = vist.ChainTransform(tf_axial)
        # Coronal :
        self.coron = ImageSection(parent=self._node_cs, name='Coronal')
        self.coron.transform = vist.ChainTransform(tf_coron)
        # Sagittal :
        self.sagit = ImageSection(parent=self._node_cs, name='Sagittal')
        self.sagit.transform = vist.ChainTransform(tf_sagit)
        # Set GL state :
        kwargs = {'depth_test': True, 'cull_face': False, 'blend': False,
                  'blend_func': ('src_alpha', 'one_minus_src_alpha')}
        self.sagit.set_gl_state('translucent', **kwargs)
        self.coron.set_gl_state('translucent', **kwargs)
        self.axial.set_gl_state('translucent', **kwargs)

    def set_cs_data(self, dx, dy, dz, bgcolor=(.2, .2, .2), alpha=0.,
                    cmap=None, radius=5., mask=0.):
        """Set data to cross-sections.

        Parameters
        ----------
        dx : int
            Offset for the sagittal image.
        dy : int
            Offset for the coronale image.
        dz : int
            Offset for the axial image.
        bgcolor : string/tuple | None
            Background color for zeros values.
        alpha : float | None
            Opacity for zeros values.
        cmap : string | None
            Colormap name.
        radius : float | 5.
            Radius of the disc intersection.
        mask : float or array_like | 0.
            Values to be potentially transparent.
        """
        # Get the colormap :
        if cmap is None:
            cmap = self._cmap_cs
        else:
            self._cmap_cs = cmap

        # Sagittal image :
        cross = [(slice(dy - 1, dy + 1), slice(None)),
                 (slice(None), slice(dz - 1, dz + 1))]
        self._set_cs_cmap(self.sagit, self.vol[dx, :, :], dx, (dy, dz),
                          cmap, radius, bgcolor, alpha, cross, mask)

        # Coronal image :
        cross = [(slice(dx - 1, dx + 1), slice(None)),
                 (slice(None), slice(dz - 1, dz + 1))]
        self._set_cs_cmap(self.coron, self.vol[:, dy, :], dy, (dx, dz),
                          cmap, radius, bgcolor, alpha, cross, mask)

        # Axial image :
        cross = [(slice(dx - 1, dx + 1), slice(None)),
                 (slice(None), slice(dy - 1, dy + 1))]
        self._set_cs_cmap(self.axial, self.vol[:, :, dz], dz, (dx, dy),
                          cmap, radius, bgcolor, alpha, cross, mask)

        # Translate images to (dx, dy, dz) :
        self._move_images(dx, dy, dz)

        self._node_cs.update()

    def _set_cs_cmap(self, obj, img, d, center, cmap, radius, bgcolor, alpha,
                     cross, mask):
        """Set the colormap to a section.

        Parameters
        ----------
        obj : ImageSection
            The ImageSection object
        img : array_like
            The 2-D image data.
        d : float
            Image offset.
        center : tuple
            A tuple of two integers where the center is located.
        cmap : string
            description
        radius : int
            Radius for the disc.
        bgcolor : tuple
            Tuple color for the background image.
        alpha : float
            Transparency level.
        cross : list
            List of slices where the cross have to be turn to black.
        mask : float or array_like | 0.
            Values to be potentially transparent.
        """
        # Find indices where img is mask :
        if isinstance(mask, (int, float)):
            img_z = img == 0
        elif isinstance(mask, np.ndarray) and (img.shape == mask.shape):
            img_z = mask
        # Get the colormap :
        img_cmap = array2colormap(img, clim=self._clim, cmap=cmap)
        # Turn image sections cross to black :
        for (k, i) in cross:
            img_cmap[k, i, 0:3] = 0.
        # Set cross-center to red :
        img_cmap[self._cs_center(img, center, radius), :] = (1., 0., 0., 1.)
        # Set colormap to image section object :
        obj.set_data(img_cmap, img_z, d)
        # Set background color and transparency :
        obj.set_color(bgcolor, alpha)

    def _cs_center(self, img, center, radius):
        """Get indices of a disc around center.

        Parameters
        ----------
        img : array_like
            The 2-D image data.
        center : tuple
            A tuple of two integers where the center is located.
        radius : int
            Radius for the disc.

        Returns
        -------
        idx : array_like
            Boolean index of the disc.
        """
        dx, dy = center
        nr, nc = img.shape
        y, x = np.ogrid[-dx:nr - dx, -dy:nc - dy]
        return x ** 2 + y ** 2 <= radius

    def _move_images(self, dx, dy, dz):
        """Move images to a defined center.

        Parameters
        ----------
        dx : int
            Offset for the sagittal image.
        dy : int
            Offset for the coronale image.
        dz : int
            Offset for the axial image.
        """
        # Sagittal image :
        tr = self._tr_sagit.translate
        self._tr_sagit.translate = (dx, tr[1], tr[2], tr[3])
        # Coronal image :
        tr = self._tr_coron.translate
        self._tr_coron.translate = (tr[0], dy, tr[2], tr[3])
        # Axial image :
        tr = self._tr_axial.translate
        self._tr_axial.translate = (tr[0], tr[1], dz, tr[3])

    # ----------- VISIBLE -----------
    @property
    def visible_cs(self):
        """Get the visible_cs value."""
        return self._visible_cs

    @visible_cs.setter
    def visible_cs(self, value):
        """Set visible_cs value."""
        self._visible_cs = value
        self._node_cs.visible = value
