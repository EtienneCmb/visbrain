from vispy.scene.visuals import create_visual_node

from .BrainMeshVisual import BrainMeshVisual
from .ConnectVisual import ConnectVisual


BrainMesh = create_visual_node(BrainMeshVisual)
Connect = create_visual_node(ConnectVisual)

__all__ = ['BrainMesh', 'Connect']