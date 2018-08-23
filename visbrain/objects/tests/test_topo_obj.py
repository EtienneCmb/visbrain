"""Test BrainObj."""
import numpy as np

from visbrain.objects import TopoObj
from visbrain.objects.tests._testing_objects import _TestObjects


# Topoplot :
channels = ['C3', 'C4', 'Cz', 'Fz', 'Pz']
data = [10, 20, 30, 10, 10]
t_obj = TopoObj('topo', data, channels=channels)


class TestTopoObj(_TestObjects):
    """Test TopoObj."""

    OBJ = t_obj

    def _get_coordinates(self):
        file = self.need_file('topoplot_data.npz')
        mat = np.load(file)
        xyz, data = mat['xyz'], mat['data']
        channels = [str(k) for k in range(len(data))]
        return xyz, data, channels

    def test_channel_definition(self):
        """Test the definition of TopoObj using channel names."""
        TopoObj('topo', data, channels=channels)

    def test_xyz_definition(self):
        """Test the definition of TopoObj using xyz coordinates."""
        xyz, data, channels = self._get_coordinates()
        TopoObj('topo', data, channels=channels, xyz=xyz)

    def test_levels(self):
        """Test levels definition."""
        xyz, data, channels = self._get_coordinates()
        # Regulary spaced levels :
        TopoObj('topo', data, channels=channels, xyz=xyz, levels=10,
                level_colors='bwr')
        # Manual levels :
        level_colors = np.array([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
        levels = [2., 2.2, 2.5]
        TopoObj('topo', data, channels=channels, xyz=xyz, levels=levels,
                level_colors=level_colors)

    def test_connect(self):
        """Test connect channels."""
        xyz, data, channels = self._get_coordinates()
        connect = (data.reshape(-1, 1) + data.reshape(1, -1)) / 2.
        select = connect < 1.97
        t_obj = TopoObj('topo', data, channels=channels, xyz=xyz)
        t_obj.connect(connect, select=select, cmap='inferno', antialias=True,
                      line_width=4.)
