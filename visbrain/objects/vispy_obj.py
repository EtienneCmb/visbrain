"""Take a VisPy visual and turn it into a compatible object."""
from vispy import scene

from .visbrain_obj import VisbrainObject


class VispyObj(VisbrainObject):
    """Take a VisPy visual and turn it into a compatible Visbrain object.

    Parameters
    ----------
    name : string
        The name of the VisPy object.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Hypnogram object parent.
    verbose : string
        Verbosity level.
    """

    def __init__(self, name, visual, transform=None, parent=None,
                 verbose=None):
        """Init."""
        VisbrainObject.__init__(self, name, parent, transform, verbose)
        visual.parent = self._node

    def _get_camera(self):
        return scene.cameras.TurntableCamera()
