"""This script contains some custom cameras behavior."""

from vispy.scene.cameras import PanZoomCamera

__all__ = ['FixedCam']


class FixedCam(PanZoomCamera):
    """Fixed camera but with all PanZoomCamera controls."""

    def __init__(self, *args, **kwargs):
        """Init."""
        PanZoomCamera.__init__(self, *args, **kwargs)

    def viewbox_mouse_event(self, event):
        """Ignore mouse event."""
        pass
