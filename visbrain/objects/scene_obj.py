"""Create a basic scene for objects."""
from vispy import scene


class SceneObj(object):
    """Create a scene for objects.

    Parameters
    ----------
    bgcolor : string | 'black'
        Background color of the scene.
    """

    def __init__(self, bgcolor='black'):
        """Init."""
        self._canvas = scene.SceneCanvas(keys='interactive', show=True,
                                         title='Object scene', bgcolor=bgcolor)
        self._grid = self._canvas.central_widget.add_grid(margin=10)

    def add_to_subplot(self, obj, row=0, col=0):
        """Add object to subplot.

        Parameters
        ----------
        obj : visbrain.object
            The visbrain object to add.
        row : int | 0
            Row location for the object.
        col : int | 0
            Columns location for the object.
        """
        try:
            cam = obj._get_camera()
        except:
            cam = 'turntable'
        sub = self._grid.add_view(row=row, col=col, camera=cam)
        sub.add(obj.parent)
