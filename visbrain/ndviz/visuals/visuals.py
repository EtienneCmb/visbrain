"""Convert user inputs and create Nd, 1d and Image objects.

This file contains the three base class for creating Nd, 1d and image object.
Each base class transform user inputs (Nd <-> nd_, 1d <-> od_, Im <-> im_) into
compatible inputs for each of the Mesh class.
Finally, the visuals class create each one of those objects then set them
parent to their corresponding canvas.
"""

from .NdpltMesh import NdpltMesh
from .OdpltMesh import OdpltMesh
# from .ImMesh import ImMesh
from vispy.scene import Node

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

        # Create a root node :
        self._vbNode = Node(name='ndviz')

        # Make this root node the parent of others ndviz objects :
        self._ndplt.mesh.parent = self._ndCanvas.wc.scene
        self._1dplt.mesh._line.parent = self._1dCanvas.wc.scene
        self._1dplt.mesh._hist.parent = self._1dCanvas.wc.scene
        self._1dplt.mesh._imag.parent = self._1dCanvas.wc.scene


class NdpltBase(object):
    """Base class for the Nd-plot.

    The main idea of this class is to manage user inputs. Basically, it turns
    the user inputs (containing nd_) into compatible inputs for the NdpltMesh
    class.
    """

    def __init__(self, data, sf, nd_axis=None, nd_color=None, nd_space=2,
                 nd_ax_name=None, nd_play=False, nd_force_col=None,
                 nd_rnd_dyn=(0.3, 0.9), nd_demean=True, nd_cmap='viridis',
                 nd_clim=None, nd_vmin=None, nd_under='gray', nd_vmax=None,
                 nd_over='red', nd_laps=1, nd_unicolor='gray', **kwargs):
        """Init."""
        self.mesh = NdpltMesh(data, sf, axis=nd_axis, color=nd_color,
                              space=nd_space, ax_name=nd_ax_name, play=nd_play,
                              force_col=nd_force_col, rnd_dyn=nd_rnd_dyn,
                              demean=nd_demean, cmap=nd_cmap, clim=nd_clim,
                              vmin=nd_vmin, under=nd_under, vmax=nd_vmax,
                              over=nd_over, laps=nd_laps, unicolor=nd_unicolor)


class OdpltBase(object):
    """Base class for the 1d-plot.

    The main idea of this class is to manage user inputs. Basically, it turns
    the user inputs (containing od_) into compatible inputs for the OdpltMesh
    class.
    """

    def __init__(self, data, sf, **kwargs):
        """Init."""
        self.mesh = OdpltMesh(data, sf, plot='line', color='uniform')


# class ImBase(ImMesh):
#     """Base class for the image-plot.

#     The main idea of this class is to manage user inputs. Basically, it turns
#     the user inputs (containing im_) into compatible inputs for the ImMesh
#     class.
#     This class inherits from the ImMesh class because the mesh object is
#     already created inside.
#     """

#     def __init__(self, data, sf, ):
#         """Init."""
#         ImMesh.__init__(self, data, sf)
