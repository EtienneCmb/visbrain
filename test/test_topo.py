"""Test Topo module and related methods."""
import numpy as np
from PyQt5 import QtWidgets
from warnings import warn
from visbrain import Topo

app = QtWidgets.QApplication([])
tp = Topo()


class TestTopo(object):
    """Test topo.py."""

    def test_add_topoplot(self):
        """Test function brain_creation."""
        name = 'Topo_1'
        channels = ['C3', 'C4', 'Cz', 'Fz', 'Pz']
        data = [10, 20, 30, 10, 10]
        title = 'Basic topoplot illustration'
        cblabel = 'Colorbar label'
        tp.add_topoplot(name, data, channels=channels, title=title,
                        cblabel=cblabel)

    def test_add_shared_colorbar(self):
        """Test function add_shared_colorbar."""
        kwargs = {'cmap': 'viridis', 'clim': (-1.02, 1.01), 'vmin': -.81,
                  'under': 'gray', 'vmax': .85, 'over': 'red'}
        tp.add_shared_colorbar('Shared', col=2, row_span=2,
                               rect=(0.1, -2, 1.6, 4),
                               cblabel='Shared colorbar', **kwargs)
