
import numpy as np
from warnings import warn
from PyQt5 import QtWidgets
import sys
from visbrain import Topo

class TestTopo(object):
    def test_topo_creation(self):
        """Test function brain_creation."""
        app = QtWidgets.QApplication([])
        vb = Topo()