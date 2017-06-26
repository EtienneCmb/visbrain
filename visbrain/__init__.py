"""
Hardware accelerated graphics for neuscientific data
====================================================

visbrain is an open-source Python software mainly dedicated to the
visualization of neuroscientific data. It's developped on top of VisPy which
provides graphic renderings offloaded to the GPU.

Right now, visbrain contains four modules :
* Brain : visualize EEG/MEG/Intracranial data and connectivity in a standard
  MNI 3D brain.
* Sleep : visualize polysomnographic data and hypnogram edition.
* Ndviz : visualize multidimensional data and basic plotting forms.
* Figure : figure-layout for high-quality publication-like figures.

See etiennecmb.github.io/visbrain for a complete and step-by step documentation
"""

from .brain.brain import Brain
from .ndviz.ndviz import Ndviz
from .sleep.sleep import Sleep
from .figure.figure import Figure
