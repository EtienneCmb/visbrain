"""Test Sleep module and related methods."""
import numpy as np
from PyQt5 import QtWidgets
from warnings import warn
from visbrain import Sleep

sf = 1000.
nelec = 8
npts = 100000

data = 10*np.random.rand(nelec, npts)
channels = ['Cz', 'Fz', 'C1', 'C2', 'C3', 'C4', 'F1', 'other']
hypno = np.random.randint(-1, 3, (npts,))

file = None
hypno_file = None

onset = np.array([100, 2000, 5000])

app = QtWidgets.QApplication([])
tp = Sleep(file=file, hypno_file=hypno_file, data=data, channels=channels,
           sf=sf, downsample=100., hypno=hypno, axis=False, hedit=False,
           annotation_file=onset)

# class TestSleep(object):
#     """Test topo.py."""
