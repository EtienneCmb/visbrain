"""Base class for objects of type Cross-sections."""
import logging
import os

import numpy as np

from vispy import scene
import vispy.visuals.transforms as vist

from ..utils import cmap_to_glsl, wrap_properties, color2vb, FixedCam
from ..io import read_nifti, niimg_to_transform
from .volume_obj import _Volume

logger = logging.getLogger('visbrain')


class _Mask(object):
    """Mask object for cross-section."""

    def __init__(self, name, parent=None, visible=False, need_cross=False,
                 deep_test=True, **_im):
        """Init."""
        self._is_defined = False
        self._vol = None
        self._cmap = None
        self._name = name
        # __________________________ IMAGES __________________________
        # Visual :
        self._im_sagit = scene.visuals.Image(name='Im_Sagit', parent=parent[0],
                                             **_im)
        self._im_coron = scene.visuals.Image(name='Im_Coron', parent=parent[1],
                                             **_im)
        self._im_axial = scene.visuals.Image(name='Im_Axial', parent=parent[2],
                                             **_im)
        # GL state :
        self._im_sagit.set_gl_state('translucent', depth_test=deep_test)
        self._im_coron.set_gl_state('translucent', depth_test=deep_test)
        self._im_axial.set_gl_state('translucent', depth_test=deep_test)

    def set_volume(self, vol, hdr):
        assert isinstance(vol, np.ndarray)
        self._vol, self._hdr, self._is_defined = vol, hdr, True
        self._sh = vol.shape
        logger.debug("%s volume set" % self._name)

    def pos_to_slice(self, pos):
        """Use the hdr transform of the mask."""
        return np.round(self._hdr.imap(pos)).astype(int)[0:-1]

    def set_slice(self, xyz):
        # Check if mask is actually used :
        if not self._is_defined:
            logger.debug("Not defined for %s" % self._name)
            return None
        # Check slice :
        sl = self.pos_to_slice(xyz)
        assert len(sl) == 3
        is_inside_vol = all([0 <= k < i for k, i in zip(sl, self._sh)])
        if not is_inside_vol:
            logger.error("Cannot set slice %s for %s" % (str(xyz), self._name))
            self._sagittal, self._coronal, self._axial = 0, 0, 0
            return None
        # Set image :
        self._im_sagit.set_data(self._vol[sl[0], ...])
        self._im_coron.set_data(self._vol[:, sl[1], :])
        self._im_axial.set_data(self._vol[..., sl[2]])
        # Get sagittal, coronal and axial sections :
        self._sagittal = int(sl[0])
        self._coronal = int(sl[1])
        self._axial = int(sl[2])

    def update(self):
        self._im_sagit.update()
        self._im_coron.update()
        self._im_axial.update()

    # ----------- CMAP -----------
    @property
    def cmap(self):
        """Get the cmap value."""
        return self._sagit.cmap

    @cmap.setter
    def cmap(self, value):
        """Set cmap value."""
        self._im_sagit.cmap = value
        self._im_coron.cmap = value
        self._im_axial.cmap = value

    # ----------- CLIM -----------
    @property
    def clim(self):
        """Get the clim value."""
        return self._clim

    @clim.setter
    def clim(self, value):
        """Set clim value."""
        self._im_sagit.clim = value
        self._im_coron.clim = value
        self._im_axial.clim = value
        self._clim = value

    # ----------- INTERPOLATION -----------
    @property
    def interpolation(self):
        """Get the interpolation value."""
        return self._interpolation

    @interpolation.setter
    def interpolation(self, value):
        """Set interpolation value."""
        self._im_sagit.interpolation = value
        self._im_coron.interpolation = value
        self._im_axial.interpolation = value
        self._interpolation = value


class CrossSecObj(_Volume):
    """Create a Cross-sections object.

    Parameters
    ----------
    name : string
        Name of the ROI object. If name is 'brodmann', 'aal' or 'talairach' a
        predefined ROI object is used and vol, index and label are ignored.
    vol : array_like | None
        The volume to use for the cross-section. Sould be an array with three
        dimensions.
    coords : tuple | None
        The MNI coordinates of the point where the cut is performed. Must
        be a tuple of three floats for (x, y, z).
    contrast : float | 0.
        The contrast of the background image 0. <= contrast <= 1.
    interpolation : string | 'nearest'
        Interpolation method for the image. See vispy.scene.visuals.Image for
        availables interpolation methods. Use 'nearest' for no interpolation.
    text_size : float | 13.
        Text size to use.
    text_color : string/tuple | 'white'
        Text color.
    text_bold : bool | True
        Use bold text.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        ROI object parent.
    verbose : string
        Verbosity level.

    Notes
    -----
    List of supported shortcuts :

        * **s** : save the figure
        * **+, -** :  Increase / decrease contrast.
        * **x, X** : Move along the x-axis.
        * **y, Y** : Move along the y-axis
        * **z, Z** : Move along the z-axis
        * **c** : Display / hide the cross.

    Examples
    --------
    >>> import numpy as np
    >>> from visbrain.objects import CrossSecObj
    >>> r = CrossSecObj('brodmann', coords=(10., -10., 20.))
    >>> r.preview(axis=True)
    """

    def __init__(self, name, vol=None, hdr=None, coords=None, contrast=0.,
                 interpolation='nearest', text_size=13., text_color='white',
                 text_bold=True, transform=None, parent=None, verbose=None,
                 preload=True, **kw):
        """Init."""
        # __________________________ VOLUME __________________________
        _Volume.__init__(self, name, parent, transform, verbose, **kw)
        self._rect = (0., -1., 2., 2.)
        self._sagittal = 0
        self._coronal = 0
        self._axial = 0
        self._latest_xyz = 0.

        # __________________________ PARENTS __________________________
        self._im_node = scene.Node(name='Images', parent=self._node)
        self._sagit_node = scene.Node(name='Sagittal', parent=self._im_node)
        self._coron_node = scene.Node(name='Coronal', parent=self._im_node)
        self._axial_node = scene.Node(name='Axial', parent=self._im_node)

        # __________________________ MASK __________________________
        kw = dict(interpolation=interpolation)
        parents = [self._sagit_node, self._coron_node, self._axial_node]
        self._bgd = _Mask('Background', parent=parents, visible=True,
                          deep_test=False, **kw)
        self._act = _Mask('Activations', parent=parents, deep_test=False, **kw)
        self._sources = _Mask('Sources', parent=parents, **kw)

        # __________________________ LOCATION __________________________
        _center = dict(pos=np.zeros((6, 3)), size=20.)
        _cross = dict(connect='segments', width=2., color='white')
        self._center = [0] * 3
        self._cross = [0] * 3
        for i, k in enumerate(parents):
            _n = k.name[0:5]
            self._center[i] = scene.visuals.Markers(name='Center_%s' % _n,
                                                    parent=k, **_center)
            self._cross[i] = scene.visuals.Line(name='Cross_%s' % _n, parent=k,
                                                **_cross)
            self._center[i].visible = False
            self._cross[i].visible = False

        # __________________________ TEXT __________________________
        self._txt_format = '%s = %.2f'
        # Add text (sagit, coron, axial, left, right) :
        txt_pos = np.array([[1.05, -.1, 0.], [1.05, -.2, 0.], [1.05, -.3, 0.],
                            [1.05, -.4, 0.], [1.05, -.5, 0.],
                            [0.05, -.1, 0.], [1.1, .9, 0.],    # L
                            [0.05, -.9, 0.], [1.9, .9, 0.]])   # R
        txt = [''] * 5 + ['L'] * 2 + ['R'] * 2
        self._txt = scene.visuals.Text(text=txt, pos=txt_pos, anchor_x='left',
                                       color=color2vb(text_color),
                                       font_size=text_size, anchor_y='bottom',
                                       bold=text_bold, parent=self._node)

        if preload:
            self(name, vol, hdr)
            self.cut_coords(coords)
            self.contrast = contrast
            self._on_key_pressed()
            self._update()

        # Set file name :
        self._set_text(0, 'File = ' + self._name)

    ###########################################################################
    ###########################################################################
    #                                  USER
    ###########################################################################
    ###########################################################################
    def cut_coords(self, coords=None):
        """Cut at a specific MNI coordinate.

        Parameters
        ----------
        coords : tuple | None
            The MNI coordinates of the point where the cut is performed. Must
            be a tuple of three floats for (x, y, z).
        """
        self._set_image(coords)

    def set_activation(self, data, xyz=None, translucent=(None, .5),
                       cmap='Spectral_r', clim=None, vmin=None, vmax=None,
                       under='red', over='green'):
        """Set any type of additional data (activation, stat...).

        Parameters
        ----------
        data : string
            Full path to the nifti file.
        xyz : array_like | None
            Coordinate of a point to center the cross-sections.
        translucent : tuple | None
            Set a specific range translucent. With f_1 and f_2 two floats, if
            translucent is :

                * (f_1, f_2) : values between f_1 and f_2 are set to
                  translucent
                * (None, f_2) x <= f_2 are set to translucent
                * (f_1, None) f_1 <= x are set to translucent
        cmap : string | 'Spectral_r'
            Colormap to use.
        clim : tuple | None
            Colorbar limits.
        vmin : float | None
            Lower threshold.
        under : string | 'red'
            Color to use for every values under vmin.
        vmax : float | None
            Over threshold.
        over : string | 'green'
            Color to use for every values over vmax.
        """
        # Load the nifti volume :
        vol, _, hdr = read_nifti(data)
        vol, hdr = self._check_volume(vol, hdr)
        tf_sagit, tf_coron, tf_axial = niimg_to_transform(vol, hdr, False,
                                                          self._vol, self._hdr)
        # Set transform :
        self._act._im_sagit.transform = tf_sagit
        tf_coron.prepend(vist.STTransform(translate=(1., 0., 0.)))
        self._act._im_coron.transform = tf_coron
        tf_axial.prepend(vist.STTransform(translate=(0., -1., 0.)))
        self._act._im_axial.transform = tf_axial
        # Set the volume and colormap :
        self._act.set_volume(vol, hdr)
        limits = (vol.min(), vol.max())
        cmap = cmap_to_glsl(limits=limits, translucent=translucent, cmap=cmap,
                            clim=clim, vmin=vmin, over=over, vmax=vmax,
                            under=under)
        self._act.cmap = cmap
        # Display activation :
        self._act._im_sagit.visible = True
        self._act._im_sagit.visible = True
        self._act._im_sagit.visible = True
        # Set activation file name :
        name = os.path.split(data)[1].split('.nii')[0]
        self._set_text(1, 'Activation = ' + name)
        # Update latest position :
        if xyz is None:
            xyz = self._latest_xyz
        self.cut_coords(xyz)
        logger.info("    Activation set using the %s file" % name)

    def localize_source(self, coords):
        """Cut at a specific MNI coordinate and display the cross.

        Parameters
        ----------
        coords : tuple | None
            The MNI coordinates of the point where the cut is performed. Must
            be a tuple of three floats for (x, y, z).
        """
        for k, i in zip(self._center, self._cross):
            k.visible = True
            i.visible = True
        self._set_image(coords, display_cross=True)

    def highlight_sources(self, xyz, radius=1, color='green'):
        """Highlight a number of sources.

        Parameters
        ----------
        xyz : array_like | None
            Array of sources coordinates. This array must have a shape of
            (n_sources, 3).
        radius : int | 1
            Default radius size to display in the IRM.
        color : string | 'green'
            Sources color.
        """
        assert isinstance(xyz, np.ndarray) and isinstance(radius, int)
        sh = self._bgd._sh
        vol = np.zeros(sh, dtype=np.float32)
        _val = 10.
        self._sources._im_sagit.transform = self._bgd._im_sagit.transform
        self._sources._im_coron.transform = self._bgd._im_coron.transform
        self._sources._im_axial.transform = self._bgd._im_axial.transform

        def f(x, sh):
            return slice(max(x, int(x - radius)), min(sh - 1, int(x + radius)))
        for k in range(xyz.shape[0]):
            sl = self.pos_to_slice(xyz[k, :])
            idx = [f(sl[0], sh[0]), f(sl[1], sh[1]), f(sl[2], sh[2])]
            vol[tuple(idx)] = _val
        self._sources.set_volume(vol, self._hdr)
        cmap = cmap_to_glsl(limits=(0., _val), translucent=(None, .5),
                            color=color)
        self._sources.cmap = cmap
        self.cut_coords(xyz[0, :])
        logger.info("    %i sources highlighted" % xyz.shape[0])

    ###########################################################################
    ###########################################################################
    #                                  DEEP
    ###########################################################################
    ###########################################################################

    def __call__(self, name, vol=None, hdr=None):
        """Change the volume object."""
        _Volume.__call__(self, name, vol=vol, hdr=hdr)
        self._bgd.set_volume(self._vol, self._hdr)
        self._grid_transform()
        self._update()

    def _get_camera(self):
        """Get the camera."""
        # cam = scene.cameras.PanZoomCamera(rect=self._rect)
        cam = FixedCam(rect=self._rect)
        cam.aspect = 1.
        return cam

    def _update(self):
        """Update the root node."""
        self._im_node.update()
        self._bgd.update()
        self._act.update()
        self._sources.update()
        self._txt.update()

    def _grid_transform(self):
        tf_sagit, tf_coron, tf_axial = niimg_to_transform(self._vol, self._hdr)
        # Sagittal transformation :
        self._bgd._im_sagit.transform = tf_sagit
        self._cross[0].transform = tf_sagit
        self._center[0].transform = tf_sagit
        # Coronal transformation :
        tf_coron.prepend(vist.STTransform(translate=(1., 0., 0.)))
        self._bgd._im_coron.transform = tf_coron
        self._cross[1].transform = tf_coron
        self._center[1].transform = tf_coron
        # Axial transformation :
        tf_axial.prepend(vist.STTransform(translate=(0., -1., 0.)))
        self._bgd._im_axial.transform = tf_axial
        self._cross[2].transform = tf_axial
        self._center[2].transform = tf_axial

    def _set_image(self, xyz, display_cross=False):
        # xyz = None -> volume center :
        if xyz is None:
            xyz = self.slice_to_pos(np.array(self._bgd._sh) / 2)
        self._latest_xyz = xyz
        # Get xyz from slices :
        sl = self.pos_to_slice(xyz)
        # ______________________ IMAGES ______________________
        self._bgd.set_slice(xyz)
        self._act.set_slice(xyz)
        self._sources.set_slice(xyz)

        # ______________________ TEXT ______________________
        # Update text :
        self._set_text(2, self._txt_format % ('x', xyz[0]))
        self._set_text(3, self._txt_format % ('y', xyz[1]))
        self._set_text(4, self._txt_format % ('z', xyz[2]))

        # ______________________ CROSS ______________________
        if display_cross:
            self._set_location(sl)

    def _set_text(self, nb, txt):
        text = self._txt.text.copy()
        text[nb] = txt
        self._txt.text = text
        self._txt.update()

    def _set_location(self, sl):
        """Set location of markers and line."""
        sh = self._sh
        # Define centers :
        _offset = 30.
        _c = np.array([[sl[2], sl[1]], [sl[2], sl[0]], [sl[1], sl[0]]])
        _c = np.c_[_c, [_offset] * 3]
        # Define lines :
        _l = np.array([[0, sl[1]], [sh[2], sl[1]], [sl[2], 0], [sl[2], sh[1]],
                       [0, sl[0]], [sh[2], sl[0]], [sl[2], 0], [sl[2], sh[0]],
                       [0, sl[0]], [sh[1], sl[0]], [sl[1], 0], [sl[1], sh[0]]])
        _l = np.c_[_l, [_offset] * 12]
        # Set centers and lines :
        for num, (k, j) in enumerate(zip(self._center, self._cross)):
            k.set_data(pos=_c[[num], :], face_color='red', edge_color='white')
            j.set_data(_l[4 * num:4 * (num + 1), :])

    ###########################################################################
    ###########################################################################
    #                                SHORTCUTS
    ###########################################################################
    ###########################################################################

    def _mouse_to_pos(self, pos):
        """Convert mouse position to pos."""
        sh = np.array(self._bgd._sh)
        if hasattr(self._node.parent.parent.camera, 'rect'):
            rect = self._node.parent.parent.camera._real_rect
        else:
            return None
        csize = self.canvas.canvas.size
        left, bottom, width, height = rect.left, rect.bottom, rect.width, \
            rect.height
        sgn = np.sign(np.diag(self._hdr.matrix))[0:-1]
        # Canvas -> [0, 1]
        x = +(pos[0] * width / csize[0]) + left
        y = -(pos[1] * height / csize[1]) - bottom
        if (0. <= x <= 1.) and (0. <= y <= 1.):
            use_idx, sl_z = [1, 2], self._bgd._sagittal
        elif (1. <= x <= 2.) and (0. <= y <= 1.):
            use_idx, sl_z = [0, 2], self._bgd._coronal
            x -= 1.
            x = x if sgn[0] == 1 else 1 - x
        elif (0. <= x <= 1.) and (-1. <= y <= 0.):
            use_idx, sl_z = [1, 0], self._bgd._axial
            y += 1.
            y = y if sgn[0] == -1 else 1 - y
        # Pixel conversion
        x_sh, y_sh = sh[use_idx]
        sl_x, sl_y = x * sh[use_idx[0]], y * sh[use_idx[1]]
        sl_xyz = np.array([sl_z] * 3)
        sl_xyz[use_idx] = [sl_x, sl_y]
        return self.slice_to_pos(sl_xyz)

    def _on_mouse_press(self):
        def on_mouse_press(event):
            """Mouse move."""
            pos = self._mouse_to_pos(event.pos)
            if pos is not None:
                self.localize_source(pos)
        return on_mouse_press

    def _on_key_pressed(self):
        # ------------------ CONTRAST ------------------
        def plus(event): self.contrast += .1  # noqa
        self.key_press['+'] = plus

        def minus(event): self.contrast -= .1  # noqa
        self.key_press['-'] = minus

        # ------------------ SECTIONS ------------------
        def sagit_plus(event): self.sagittal = self._bgd._sagittal - 1  # noqa
        self.key_press['X'] = sagit_plus

        def sagit_less(event): self.sagittal = self._bgd._sagittal + 1  # noqa
        self.key_press['x'] = sagit_less

        def coron_plus(event): self.coronal = self._bgd._coronal - 1  # noqa
        self.key_press['Y'] = coron_plus

        def coron_less(event): self.coronal = self._bgd._coronal + 1  # noqa
        self.key_press['y'] = coron_less

        def axial_plus(event): self.axial = self._bgd._axial - 1  # noqa
        self.key_press['Z'] = axial_plus

        def axial_less(event): self.axial = self._bgd._axial + 1  # noqa
        self.key_press['z'] = axial_less

        # ------------------ CROSS ------------------
        def cross(event):
            is_visible = not self._center[0].visible
            for k, i in zip(self._center, self._cross):
                k.visible = is_visible
                i.visible = is_visible
        self.key_press['c'] = cross

    ###########################################################################
    ###########################################################################
    #                                PROPERTIES
    ###########################################################################
    ###########################################################################
    # ----------- SAGITTAL -----------
    @property
    def sagittal(self):
        """Get the sagittal value."""
        return self._sagittal

    @sagittal.setter
    def sagittal(self, value):
        """Set sagittal value."""
        if not isinstance(value, int) and (self._sagittal != value):
            logger.error("Cannot set sagittal %s" % value)
            return None
        x = self.slice_to_pos((value, self._bgd._coronal, self._bgd._axial))
        self._set_image(x)
        self._sagittal = value

    # ----------- CORONAL -----------
    @property
    def coronal(self):
        """Get the coronal value."""
        return self._coronal

    @coronal.setter
    def coronal(self, value):
        """Set coronal value."""
        if not isinstance(value, int) and (self._coronal != value):
            logger.error("Cannot set coronal %s" % value)
            return None
        y = self.slice_to_pos((self._bgd._sagittal, value, self._bgd._axial))
        self._set_image(y)
        self._coronal = value

    # ----------- AXIAL -----------
    @property
    def axial(self):
        """Get the axial value."""
        return self._axial

    @axial.setter
    def axial(self, value):
        """Set axial value."""
        if not isinstance(value, int) and (self._axial != value):
            logger.error("Cannot set axial %s" % value)
            return None
        z = self.slice_to_pos((self._bgd._sagittal, self._bgd._coronal, value))
        self._set_image(z)
        self._axial = value

    # ----------- CONTRAST -----------
    @property
    def contrast(self):
        """Get the contrast value."""
        return self._contrast

    @contrast.setter
    def contrast(self, value):
        """Set contrast value."""
        if (value < 0.) or (value > 1.):
            logger.error("Contrast must be between [0, 1]")
            return None
        clim = (self._vol.min() * (1. + value), self._vol.max() * (1. - value))
        limits = (self._vol.min(), self._vol.max())
        self._bgd.cmap = cmap_to_glsl(limits=limits, clim=clim, cmap='Greys_r')
        self._bgd.clim = 'auto'
        self._contrast = value

    # ----------- TEXT_SIZE -----------
    @property
    def text_size(self):
        """Get the text_size value."""
        return self._text_size

    @text_size.setter
    @wrap_properties
    def text_size(self, value):
        """Set text_size value."""
        assert isinstance(value, (int, float))
        self._text_size = value
        self._txt.font_size = value
        self._txt.update()

    # ----------- INTERPOLATION -----------
    @property
    def interpolation(self):
        """Get the interpolation value."""
        return self._im_sagit.interpolation

    @interpolation.setter
    @wrap_properties
    def interpolation(self, value):
        """Set interpolation value."""
        assert isinstance(value, str)
        self._bgd.interpolation = value
        self._act.interpolation = value
        self._sources.interpolation = value
        self._update()
