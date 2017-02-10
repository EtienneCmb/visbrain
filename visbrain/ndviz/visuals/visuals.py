"""
"""

from .NdpltBase import NdpltBase
from .OdpltMesh import OdpltMesh
from vispy.scene import Node


class visuals(object):
    """
    """

    def __init__(self, data, sf, **kwargs):
        """Init."""
        self._ndplt = NdpltBase(data, sf, **kwargs)
        self._1dplt = OdpltMesh(data, sf, xtype='time', plot='histogram', color='slateblue')

        # Create a root node :
        self._vbNode = Node(name='ndviz')

        # Make this root node the parent of others ndviz objects :
        self._ndplt.mesh.parent = self._ndCanvas.wc.scene
        self._1dplt.mesh.parent = self._1dCanvas.wc.scene
        # self._ndplt.mesh.parent = self._vbNode
