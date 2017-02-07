"""Transform an visual objects into a vispy node.

This make it easier to add vispy transformations.
"""

from vispy.scene.visuals import create_visual_node

from .BrainVisual import BrainVisual
from .ConnectVisual import ConnectVisual


BrainMesh = create_visual_node(BrainVisual)
ConnectMesh = create_visual_node(ConnectVisual)

__all__ = ['BrainMesh', 'ConnectMesh']
