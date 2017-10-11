"""Main class for Visbrain objects."""
import vispy
import sys

from ..visuals import VisbrainCanvas


class VisbrainObject(object):
    """Base class inherited by all of the Visbrain objects."""

    def __init__(self, name, parent, prev_camera='turntable'):
        """Init."""
        self._prev_camera = prev_camera
        self._node = vispy.scene.Node(name=type(self).__name__)
        self._node.parent = parent
        # Name :
        assert isinstance(name, str)
        self._name = name

    def __repr__(self):
        """Represent ClassName(name='object_name')."""
        return type(self).__name__ + "(name='" + self._name + "')"

    def __str__(self):
        """Return the object name."""
        return self._name

    def preview(self, bgcolor='white', axis=True):
        """Previsualize the result.

        Parameters
        ----------
        bgcolor : array_like/string/tuple | 'white'
            Background color for the preview.
        """
        assert self._prev_camera in ['turntable', 'panzoom']
        canvas = VisbrainCanvas(axis=axis, show=True, title=self._name,
                                bgcolor=bgcolor)
        self._node.parent = canvas.wc.scene
        # canvas.camera = self._prev_camera
        canvas.camera = self._get_camera()
        canvas.camera.center = self._xyz.mean(axis=0)
        # vispy.scene.visuals.XYZAxis(parent=canvas.wc.scene)
        # view.camera = camera
        if sys.flags.interactive != 1:
            vispy.app.run()
