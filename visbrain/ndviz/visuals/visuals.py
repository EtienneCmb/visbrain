"""Convert user inputs and create Nd, 1d and Image objects.

This file contains the three base class for creating Nd, 1d and image object.
Each base class transform user inputs (Nd <-> nd_, 1d <-> od_, Im <-> im_) into
compatible inputs for each of the Mesh class.
Finally, the visuals class create each one of those objects then set them
parent to their corresponding canvas.
"""

from .NdpltMesh import NdpltMesh
from .OdpltMesh import OdpltMesh
from ...utils import vis_args

__all__ = ["visuals"]


class visuals(object):
    """Create the visual objects to be added to the scene.

    This class create a Nd-plot, 1d-plot and Image-plot objects and set them
    parents on their own canvas.
    """

    def __init__(self, data, sf, **kwargs):
        """Init."""
        self._ndplt = NdpltBase(data, sf, **kwargs)
        self._1dplt = OdpltBase(data, sf, **kwargs)

        # Make this root node the parent of others ndviz objects :
        self._ndplt.mesh.parent = self._ndCanvas.wc.scene
        self._1dplt.mesh.parent = self._1dCanvas.wc.scene


class NdpltBase(object):
    """Base class for the Nd-plot.

    The main idea of this class is to manage user inputs. Basically, it turns
    the user inputs (containing nd_) into compatible inputs for the NdpltMesh
    class.
    """

    def __getitem__(self, name):
        """Get a variable"""
        pass

    def __init__(self, data, sf, **kwargs):
        """Init."""
        # Get arguments starting with 'nd_' :
        ignore = ['nd_grid']
        self._ndargs, _ = vis_args(kwargs, 'nd_', ignore)
        self.mesh = NdpltMesh(data, sf, **self._ndargs)


class OdpltBase(object):
    """Base class for the 1d-plot.

    The main idea of this class is to manage user inputs. Basically, it turns
    the user inputs (containing od_) into compatible inputs for the OdpltMesh
    class.
    """

    def __init__(self, data, sf, **kwargs):
        """Init."""
        # Get arguments starting with 'od_' :
        ignore = ['od_grid']
        args, _ = vis_args(kwargs, 'od_', ignore)
        self.mesh = OdpltMesh(data, sf)
        self.mesh.set_data(data, sf, **args)
