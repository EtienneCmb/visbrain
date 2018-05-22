"""
Hardware accelerated graphics for neuscientific data
====================================================

visbrain is an open-source Python software mainly dedicated to the
visualization of neuroscientific data. It's developped on top of VisPy which
provides graphic renderings offloaded to the GPU.

Right now, visbrain contains five modules :
* Brain : visualize EEG/MEG/Intracranial data and connectivity in a standard
  MNI 3D brain.
* Sleep : visualize polysomnographic data and hypnogram edition.
* Signal : data mining module for signal inspection.
* Figure : figure-layout for high-quality publication-like figures.
* Colorbar : a colorbar editor
* Topo : topographic representations

See http://visbrain.org/ for a complete and step-by step documentation
"""
import sys

# Import modules :
from .brain import Brain
from .colorbar import Colorbar
from .figure import Figure
from .sleep import Sleep
from .topo import Topo
from .signal import Signal

__all__ = ['Brain', 'Colorbar', 'Figure', 'Signal', 'Sleep', 'Topo']
__version__ = "0.4.0"


# PyQt5 crash if an error occured. This small function fix it for all modules
# to retrieve the PyQt4 behavior :


def pyqt4_behavior(type, value, tback):
    """Retrieve PyQt4 behavior if an error occured."""
    sys.__excepthook__(type, value, tback)


sys.excepthook = pyqt4_behavior
