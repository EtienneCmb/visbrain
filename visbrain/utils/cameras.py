"""This script contains some custom cameras behavior."""
import logging
import numpy as np

from vispy.scene.cameras import PanZoomCamera, TurntableCamera, BaseCamera

__all__ = ['FixedCam', 'ScrollCamera', 'rotate_turntable',
           'optimal_scale_factor', 'merge_cameras']

logger = logging.getLogger('visbrain')


class FixedCam(PanZoomCamera):
    """Fixed camera but with all PanZoomCamera controls."""

    def __init__(self, *args, **kwargs):
        """Init."""
        PanZoomCamera.__init__(self, *args, **kwargs)

    def viewbox_mouse_event(self, event):
        """Ignore mouse event."""
        pass


class ScrollCamera(PanZoomCamera):
    """Scrolling camera.

    Parameters
    ----------
    args : tuple
        Arguments to pass to the PanZoom camera.
    sc_axis : {'x', 'y'}
        Scrolling axes.
    limits : tuple | None
        Tuple of floats describing the axis limits.
    smooth : float | 1.
        Scrolling smooth factor. Higher values can be used to reduce the
        scrolling.
    kwargs : dict | {}
        Optional arguments to pass to the PanZoom camera.
    """

    def __init__(self, *args, sc_axis='x', limits=None, smooth=1., **kwargs):
        """Init."""
        PanZoomCamera.__init__(self, *args, **kwargs)

        self._ax = 0 if sc_axis == 'x' else 1
        self._limits = limits
        self._smooth = smooth

    def viewbox_mouse_event(self, event):
        """Ignore mouse event."""
        if event.handled or not self.interactive:
            return

        # Scrolling
        BaseCamera.viewbox_mouse_event(self, event)

        if event.type == 'mouse_wheel':
            pos = list(self.rect.pos)
            ax = self._ax
            pos[ax] = pos[ax] + event.delta[1] / self._smooth
            if isinstance(self._limits, (list, tuple)):
                if not (self._limits[0] <= pos[ax] <= self._limits[1]):
                    return
            size = self.rect.size
            self.rect = (pos[0], pos[1], size[0], size[1])
        elif event.type == 'mouse_move':
            if event.press_event is None:
                return

            modifiers = event.mouse_event.modifiers
            if 2 in event.buttons and not modifiers:
                # Zoom
                p1c = np.array(event.last_event.pos)[:2]
                p2c = np.array(event.pos)[:2]
                scale = ((1 + self.zoom_factor) **
                         ((p1c - p2c) * np.array([1, -1])))
                center = self._transform.imap(event.press_event.pos[:2])
                self.zoom(scale, center)
                event.handled = True
            else:
                event.handled = False
        elif event.type == 'mouse_press':
            # accept the event if it is button 1 or 2.
            # This is required in order to receive future events
            event.handled = event.button in [1, 2]
        else:
            event.handled = False


def _default_cam_config(use_for, values):
    for k in use_for:
        FIXED_CAM[k] = values


FIXED_CAM = {}
_default_cam_config(['left', 'sagittal_0', 'sagittal'], (-90., 0., [1, 2], -1))
_default_cam_config(['right', 'sagittal_1'], (90., 0., [1, 2], -1))
_default_cam_config(['front', 'coronal_0', 'coronal'], (180., 0., [0, 2], -1))
_default_cam_config(['back', 'coronal_1'], (0., 0., [0, 2], -1))
_default_cam_config(['top', 'axial_0', 'axial'], (0., 90., [0, 1], 1))
_default_cam_config(['bottom', 'axial_1'], (0., -90., [0, 1], 1))


def rotate_turntable(fixed=None, camera_state={}, camera=None,
                     xyz=None, csize=None, margin=1., _scale=1.):
    """Rotate a scene that contains a turntable camera.

    Parameters
    ----------
    fixed : {'left', 'right', 'front', 'back', 'top', 'bottom'}
        Fixed rotation.
    camera_state : dict | {}
        Dictionary to pass to the camera.
    camera : vispy.scene.cameras.TurntableCamera | None
        The camera to update.
    xyz : array_like | None
        The size of the object along the x, y and z axis.
    csize : tuple | None
        The canvas size.
    margin : float | 1.
        Add magin to the scale_factor.
    _scale : float | 1.
        Specifie if the scale_factor have to be rescaled.

    Returns
    -------
    camera_state : dict
        The camera state used.
    """
    assert all([isinstance(k, (int, float)) for k in [margin, _scale]])
    if isinstance(fixed, str):
        azimuth, elevation, idx, priority = FIXED_CAM[fixed]
        camera_state['azimuth'] = azimuth
        camera_state['elevation'] = elevation
    if (xyz is not None) and (len(xyz) == 3):
        xyz = np.asarray(xyz)
        if csize is None:
            camera_state['scale_factor'] = xyz[priority]
        else:
            logger.debug("Optimal scale factor using %r axis" % idx)
            assert len(csize) == 2
            sc = xyz[idx]
            camera_state['scale_factor'] = optimal_scale_factor(sc, csize)
    if 'scale_factor' in camera_state:
        camera_state['scale_factor'] *= _scale * margin
    if camera_state and isinstance(camera, TurntableCamera):
        if 'distance' in camera_state.keys():
            dist = camera_state.pop('distance')
            camera.distance = dist
        camera.set_state(**camera_state)
    return camera_state


def optimal_scale_factor(axis_scale, csize):
    """Get optimal scale_factor according to screen size.

    Parameters
    ----------
    axis_scale : array_like
        The scale along the two axis.
    csize : tuple
        The canvas size.
    """
    assert len(axis_scale) == len(csize)
    x_ratio = axis_scale[0] / csize[0]
    y_ratio = axis_scale[1] / csize[1]
    # Get the optimal scaling factor :
    opt_scale_factor = axis_scale[np.argmax([x_ratio, y_ratio])]
    return opt_scale_factor


def merge_cameras(*args):
    """Merge several TurnTable cameras.

    This function returns the mean center and the max across scale_factor and
    distances.

    Parameter
    ---------
    args : TurnTableCamera
        The turntable cameras to use.

    Returns
    -------
    cam_state : dict
        The dictionary of merged camera states.
    """
    assert all([isinstance(k, TurntableCamera) for k in args])
    center = np.zeros((3,), dtype=np.float32)
    scale_factor, distance = [], []
    # Get the camera state of multiple cameras :
    for k in args:
        cam_state = k.get_state()
        center += cam_state['center']
        scale_factor.append(cam_state['scale_factor'])
        if isinstance(k.distance, (int, float)):
            distance.append(k.distance)
    # Get mean center, max scale_factor and max distance :
    center /= len(args)
    scale_factor = np.max(scale_factor)
    distance = np.max(distance) if len(distance) else None
    # Create turntable camera :
    cam = TurntableCamera(center=center, scale_factor=scale_factor,
                          distance=distance)
    return cam
