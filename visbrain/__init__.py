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
* Ndviz : visualize multidimensional data and basic plotting forms.
* Figure : figure-layout for high-quality publication-like figures.
* Colorbar : a colorbar editor

See etiennecmb.github.io/visbrain for a complete and step-by step documentation
"""
import sys

# Import modules :
from .brain import Brain
from .colorbar import Colorbar
from .figure import Figure
from .ndviz import Ndviz
from .sleep import Sleep
from .topo import Topo

__all__ = ['Brain', 'Colorbar', 'Figure', 'Ndviz', 'Sleep', 'Topo']
__version__ = "0.3.3"

# PyQt5 crash if an error occured. This small function fix it for all modules
# to retrieve the PyQt4 behavior :


def PyQt4_behavior(type, value, tback):
    """Retrieve PyQt4 behavior if an error occured."""
    sys.__excepthook__(type, value, tback)


sys.excepthook = PyQt4_behavior
