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

from .brain import Brain
from .ndviz import Ndviz
from .sleep import Sleep
from .figure import Figure
from .colorbar import Colorbar
