"""Base class for objects of type Cross-sections."""
import logging

import numpy as np

from vispy import scene
import vispy.visuals.transforms as vist

from ..utils import cmap_to_glsl, wrap_properties, color2vb, FixedCam
from ..io import read_nifti
from .volume_obj import _Volume

logger = logging.getLogger('visbrain')


class _ImageSection(object):
    """Image section.

    This class instantiate an image, markers and line for source location.
    """

    def __init__(self, name, parent=None, loc_parent=None, act_parent=None,
                 _im={}, _mark={}, _line={}):
        """Init."""
        # Background image :
        self.node = scene.Node(name='Node_', parent=parent)
        self.act_node = scene.Node(name='ActNode_', parent=act_parent)
        self.image = scene.visuals.Image(name='Im_' + name, parent=self.node,
                                         cmap='grays', **_im)
        # Activation :
        cmap = cmap_to_glsl(cmap='Spectral_r')
        self.image_act = scene.visuals.Image(name='ImAct_' + name,
                                             parent=self.act_node,
                                             cmap='viridis', **_im)
        self.image_act.cmap = cmap
        # self.act_node.visible = False
        # Location :
        pos = np.zeros((10, 3))
        self.loc_node = scene.Node(name='LocNode_', parent=loc_parent)
        self.markers = scene.visuals.Markers(pos=pos, name='Mark_' + name,
                                             parent=self.loc_node, **_mark)
        self.line = scene.visuals.Line(name='Line_' + name, connect='segments',
                                       parent=self.loc_node, **_line)

    def set_location(self, center, offset=10., limits=(0, 1)):
        """Set location of markers and line."""
        # Set marker :
        center.append(offset)
        self.markers.set_data(pos=np.array(center).reshape(1, -1),
                              face_color='red')
        # Set line :
        pos = np.array([[0, center[1]], [limits[0], center[1]],
                        [center[0], 0], [center[0], limits[1]]])
        pos = np.c_[pos, [10.] * 4]
        self.line.set_data(pos=pos)

    def update(self):
        self.node.update()
        self.loc_node.update()
        self.image.update()
        self.image_act.update()
        self.markers.update()
        self.line.update()

    # ----------- TRANSFORM -----------
    @property
    def transform(self):
        """Get the transform value."""
        return self.node.transform

    @transform.setter
    def transform(self, value):
        """Set transform value."""
        self.node.transform = value
        self.act_node.transform = value
        self.loc_node.transform = value


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
    section : tuple | None
        The section to take (sagittal, coronal and axial slices). Must be a
        tuple of integers.
    interpolation : string | 'nearest'
        Interpolation method for the image. See vispy.scene.visuals.Image for
        availables interpolation methods.
    text_size : float | 15.
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
    kw : dict | {}
        Optional arguments are used to control the colorbar
        (See :class:`ColorbarObj`).

    Examples
    --------
    >>> import numpy as np
    >>> from visbrain.objects import CrossSecObj
    >>> r = CrossSecObj('brodmann', section=(10, -10, 20))
    >>> r.preview(axis=True)
    """

    ###########################################################################
    ###########################################################################
    #                                BUILT IN
    ###########################################################################
    ###########################################################################

    def __init__(self, name, vol=None, hdr=None, section=None, contrast=.3,
                 interpolation='bilinear', text_size=15., text_color='white',
                 text_bold=True, transform=None, parent=None, verbose=None,
                 preload=True, **kw):
        """Init."""
        # __________________________ VOLUME __________________________
        _Volume.__init__(self, name, parent, transform, verbose, **kw)
        self._sagittal = 0
        self._coronal = 0
        self._axial = 0
        # __________________________ PARENTS __________________________
        self._act_node = scene.Node(name='Act_', parent=self._node)
        self._im_node = scene.Node(name='Im_', parent=self._node)
        self._loc_node = scene.Node(name='Loc_', parent=self._node)
        self._act_node.visible = False
        self._loc_node.visible = False

        # __________________________ TRANSFORMATION __________________________
        # Define three images (Sagittal, Coronal, Axial), markers and line :
        kwi = dict(parent=self._im_node, loc_parent=self._loc_node,
                   act_parent=self._act_node,
                   _im=dict(interpolation=interpolation), _mark=dict(size=20.),
                   _line=dict(width=3., color='white'))
        self._im_sagit = _ImageSection('Sagit', **kwi)
        self._im_coron = _ImageSection('Coron', **kwi)
        self._im_axial = _ImageSection('Axial', **kwi)
        # Add text (sagit, coron, axial, left, right) :
        txt_pos = np.array([[-.99, -.1, 0.], [.01, -.1, 0.], [-.99, -1.99, 0.],
                            [.9, -.2, 0.], [0.1, .9, 0.], [.9, -1.8, 0.],
                            [0.9, .9, 0.]])
        txt = ['Text'] * 3 + ['L'] * 2 + ['R'] * 2
        self._txt = scene.visuals.Text(text=txt, pos=txt_pos, anchor_x='left',
                                       color=color2vb(text_color),
                                       font_size=text_size, anchor_y='bottom',
                                       bold=text_bold, parent=self._node)

        if preload:
            self(name, vol, hdr)
            self.set_data(section=section, **kw)
            self.contrast = contrast
            self._on_key_pressed()

    def __call__(self, name, vol=None, hdr=None):
        """Change the volume object."""
        _Volume.__call__(self, name, vol=vol, hdr=hdr)
        self._define_transformation()
        self.update()

    def _define_transformation(self):
        sh = self._sh
        rz90 = vist.MatrixTransform()
        rz90.rotate(90, (0, 0, 1))
        rx180 = vist.MatrixTransform()
        rx180.rotate(180, (1, 0, 0))
        # Sagittal transformation :
        norm_sagit = vist.STTransform(scale=(1. / sh[1], 1. / sh[2], 1.),
                                      translate=(-1., 0., 0.))
        tf_sagit = vist.ChainTransform([norm_sagit, rz90, rx180])
        self._im_sagit.transform = tf_sagit
        # Coronal transformation :
        norm_coron = vist.STTransform(scale=(1. / sh[0], 1. / sh[2], 1.),
                                      translate=(0., 0., 0.))
        tf_coron = vist.ChainTransform([norm_coron, rz90, rx180])
        self._im_coron.transform = tf_coron
        # Axial transformation :
        norm_axis = vist.STTransform(scale=(2. / sh[1], 2. / sh[0], 1.),
                                     translate=(-1., 0., 0.))
        tf_axial = vist.ChainTransform([norm_axis, rx180])
        self._im_axial.transform = tf_axial

    def _get_camera(self):
        """Get the camera."""
        cam = scene.cameras.PanZoomCamera(rect=(-1.5, -2., 3., 3.))
        # cam = FixedCam(rect=(-1.5, -2., 3., 3.))
        return cam

    def _get_bg_cmap(self, clim=None):
        """Get the default background colormap."""
        limits = (self._vol.min(), self._vol.max())
        return cmap_to_glsl(limits=limits, clim=clim, cmap='Greys_r')

    def update(self):
        """Update the root node."""
        self._im_node.update()
        self._loc_node.update()
        self._im_sagit.update()
        self._im_coron.update()
        self._im_axial.update()
        self._txt.update()

    def set_data(self, section=None, clim=None, cmap=None, vmin=None,
                 under=None, vmax=None, over=None, update=False):
        """Set data to the cross-section.

        Parameters
        ----------
        section : tuple | (0, 0, 0)
            The section to take (sagittal, coronal and axial slices).
        """
        if section is None:
            section = [int(k) for k in self.pos_to_slice([0., 0., 0.])]
        assert len(section) == 3 and all([k <= i for k, i in zip(section,
                                                                 self._sh)])
        self._section = section
        clim = (self._vol.min(), self._vol.max()) if clim is None else clim
        _ = self._update_cbar_args(cmap, clim, vmin, vmax, under, over)  # noqa
        self._update = update
        self.sagittal = section[0]
        self.coronal = section[1]
        self.axial = section[2]
        self._update = False

    def set_activation(self, data, xyz=None, **kwargs):
        """"""
        vol, _, hdr = read_nifti(data)
        vol, hdr = self._check_volume(vol, hdr)
        fact = [k / i for k, i in zip(self._vol.shape, vol.shape)]

        if xyz is None:
            xyz = (self._sagittal, self._coronal, self._axial)
            xyz = self.pos_to_slice(xyz)
        sl = self.pos_to_slice(xyz, hdr=hdr)
        self.localize_source(xyz)

        # Sagittal :
        tf_sagit = vist.STTransform(scale=(fact[2], fact[1], 1.))
        self._im_sagit.image_act.transform = tf_sagit
        self._im_sagit.image_act.set_data(vol[sl[0], ...])
        # Coronal :
        tf_coron = vist.STTransform(scale=(fact[2], fact[0], 1.))
        self._im_coron.image_act.set_data(vol[:, sl[1], :])
        self._im_coron.image_act.transform = tf_coron
        # Axial :
        tf_axial = vist.STTransform(scale=(fact[1], fact[0], 1.))
        self._im_axial.image_act.set_data(vol[..., sl[2]])
        self._im_axial.image_act.transform = tf_axial
        self._act_node.visible = True
        self.update()

    def _set_section(self, im_visual, image, pos, nb, dim):
        # Set image and text :
        im_visual.image.set_data(image)
        txt = '%s=%.2f'
        text = self._txt.text.copy()
        text[nb] = txt % (dim, pos)
        self._txt.text = text
        self.update()

    def localize_source(self, xyz):
        """Center the cross-sections arround a source location.

        Parameters
        ----------
        xyz : array_like
            The (x, y, z) location of the source. Could be a tuple, list or an
            array.
        """
        # Convert position into slice :
        sl = self.pos_to_slice(xyz)
        logger.info("Center cross-sections at position %s" % str(xyz))
        # Set image slices :
        self.sagittal = int(sl[0])
        self.coronal = int(sl[1])
        self.axial = int(sl[2])
        # Set location centers :
        sh = np.array(self._sh)
        self._im_sagit.set_location([sl[2], sl[1]], limits=sh[[2, 1]])
        self._im_coron.set_location([sl[2], sl[0]], limits=sh[[2, 0]])
        self._im_axial.set_location([sl[1], sl[0]], limits=sh[[1, 0]])
        self._loc_node.visible = True
        self.update()

    def _mouse_to_pos(self, pos):
        """Convert mouse position to pos."""
        sh = np.array(self._sh)
        csize = self.canvas.canvas.size
        rect = (-1.5, -2., 3., 3.)
        idx_xy = None
        # Canvas -> camera conversion :
        x = +(pos[0] * rect[2] / csize[0]) + rect[0]
        y = -(pos[1] * rect[3] / csize[1]) - rect[1]
        if (-1. <= x <= 0.) and (1. <= y):
            idx_xy, sl_z = [1, 2], self.sagittal
            x_off, x_lim, y_off, y_lim, y_inv = 1., 0., -1., 0., 1.
        elif (0. <= x <= 1.) and (1. <= y):
            idx_xy, sl_z = [0, 2], self.coronal
            x_off, x_lim, y_off, y_lim, y_inv = 0., 0., -1., 0., 1.
        elif (-1. <= x <= 1.) and (y <= 1.):
            idx_xy, sl_z = [1, 0], self.axial
            x_off, x_lim, y_off, y_lim, y_inv = 1., 1., 1., 1., -1.
        # Camera -> pos conversion :
        if idx_xy is None:  # out of picture
            return None
        pic = sh[idx_xy]
        sl_x = (rect[2] * (+x + x_off) * pic[0]) / ((1. + x_lim) * rect[2])
        sl_y = (rect[3] * (y_inv * y + y_off) * pic[1]) / \
            ((1. + y_lim) * rect[3])
        sl_xyz = np.array([sl_z] * 3)
        sl_xyz[idx_xy] = [sl_x, sl_y]
        return self.slice_to_pos(sl_xyz)

    def _on_mouse_press(self):
        def on_mouse_press(event):
            """Mouse move."""
            pos = self._mouse_to_pos(event.pos)
            if pos is not None:
                self.localize_source(pos)
        return on_mouse_press

    def _on_key_pressed(self):
        def plus(event):  # noqa
            self.contrast += .1

        def minus(event):  # noqa
            self.contrast -= .1
        self.key_press['+'] = plus
        self.key_press['-'] = minus

    # ----------- SAGITTAL -----------
    @property
    def sagittal(self):
        """Get the sagittal value."""
        return self._sagittal

    @sagittal.setter
    def sagittal(self, value):
        """Set sagittal value."""
        val_cond = value != self._sagittal and isinstance(value, int)
        if val_cond or self._update:
            if value <= self._sh[0]:
                pos = self.slice_to_pos(value, axis=0)
                self._set_section(self._im_sagit, self._vol[value, ...], pos,
                                  0, 'x')
                self._sagittal = value
            else:
                logger.error("Cannot take sagittal section %s. Max across "
                             "first dimension is %s." % (value, self._sh[0]))

    # ----------- CORONAL -----------
    @property
    def coronal(self):
        """Get the coronal value."""
        return self._coronal

    @coronal.setter
    def coronal(self, value):
        """Set coronal value."""
        val_cond = value != self._coronal and isinstance(value, int)
        if val_cond or self._update:
            if value <= self._sh[1]:
                pos = self.slice_to_pos(value, axis=1)
                self._set_section(self._im_coron, self._vol[:, value, :],
                                  pos, 1, 'y')
                self._coronal = value
            else:
                logger.error("Cannot take coronal section %s. Max across "
                             "second dimension is %s." % (value, self._sh[1]))

    # ----------- AXIAL -----------
    @property
    def axial(self):
        """Get the axial value."""
        return self._axial

    @axial.setter
    def axial(self, value):
        """Set axial value."""
        val_cond = value != self._axial and isinstance(value, int)
        if val_cond or self._update:
            if value <= self._sh[2]:
                pos = self.slice_to_pos(value, axis=2)
                self._set_section(self._im_axial, self._vol[..., value],
                                  pos, 2, 'z')
                self._axial = value
            else:
                logger.error("Cannot take axial section %s. Max across "
                             "third dimension is %s." % (value, self._sh[2]))

    # ----------- CONTRAST -----------
    @property
    def contrast(self):
        """Get the contrast value."""
        return self._contrast

    @contrast.setter
    def contrast(self, value):
        """Set contrast value."""
        assert 0. <= value < 1.
        clim = (self._vol.min() * (1. + value), self._vol.max() * (1. - value))
        cmap = self._get_bg_cmap(clim=clim)
        self._im_sagit.image.cmap = cmap
        self._im_coron.image.cmap = cmap
        self._im_axial.image.cmap = cmap
        self._contrast = value

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
        self._im_sagit.interpolation = value
        self._im_coron.interpolation = value
        self._im_axial.interpolation = value
        self.update()

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
