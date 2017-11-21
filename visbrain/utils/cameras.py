"""This script contains some custom cameras behavior."""

from vispy.scene.cameras import PanZoomCamera, TurntableCamera

__all__ = ['FixedCam', 'rotate_turntable']


class FixedCam(PanZoomCamera):
    """Fixed camera but with all PanZoomCamera controls."""

    def __init__(self, *args, **kwargs):
        """Init."""
        PanZoomCamera.__init__(self, *args, **kwargs)

    def viewbox_mouse_event(self, event):
        """Ignore mouse event."""
        pass


def rotate_turntable(fixed=None, camera_state={}, camera=None):
    """Rotate a scene that contains a turntable camera.

    Parameters
    ----------
    fixed : {'left', 'right', 'front', 'back', 'top', 'bottom'}
        Fixed rotation.
    camera_state : dict | {}
        Dictionary to pass to the camera.
    camera : vispy.scene.cameras.TurntableCamera | None
        The camera to update.

    Returns
    -------
    camera_state : dict
        The camera state used.
    """
    if isinstance(fixed, str):
        if fixed in ['sagittal_0', 'left']:     # left
            azimuth, elevation = -90, 0
        elif fixed in ['sagittal_1', 'right']:  # right
            azimuth, elevation = 90, 0
        elif fixed in ['coronal_0', 'front']:   # front
            azimuth, elevation = 180, 0
        elif fixed in ['coronal_1', 'back']:    # back
            azimuth, elevation = 0, 0
        elif fixed in ['axial_0', 'top']:       # top
            azimuth, elevation = 0, 90
        elif fixed in ['axial_1', 'bottom']:    # bottom
            azimuth, elevation = 0, -90
        camera_state['azimuth'] = azimuth
        camera_state['elevation'] = elevation
    if camera_state and isinstance(camera, TurntableCamera):
        camera.set_state(**camera_state)
    return camera_state
