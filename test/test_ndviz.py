"""Test Ndviz module and related methods."""
from PyQt5 import QtWidgets
import numpy as np

from visbrain import Ndviz

kw = {}
kw['sf'] = 1024.
y = np.random.rand(10, 20, 3).astype(np.float32)

# ---------------- Application  ----------------
app = QtWidgets.QApplication([])
vb = Ndviz(y, **kw)
