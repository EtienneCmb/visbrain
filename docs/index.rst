.. image:: https://travis-ci.org/EtienneCmb/visbrain.svg?branch=master
    :target: https://travis-ci.org/EtienneCmb/visbrain

.. image:: https://codecov.io/gh/EtienneCmb/visbrain/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/EtienneCmb/visbrain

.. image:: https://badge.fury.io/py/visbrain.svg
  :target: https://badge.fury.io/py/visbrain

.. Levels :
.. # Main title
.. * Tile 1
.. = Title 2
.. - Title 3
.. ~ Title 4
.. ^ Title 5
.. + Title 6

Visbrain documentation
######################

Visbrain is a python 3 package dedicated to multi-purpose neuroscience visualization tools. Here is the list of the current modules :

.. figure::  /picture/visbrain_readme.png
   :align:   center

* :ref:`Brain` : visualize EEG/MEG/Intracranial data, connectivity in a standard MNI 3D brain (see `Brain examples <http://visbrain.org/auto_examples/index.html#brain-examples>`_).
* :ref:`Sleep` : visualize polysomnographic data and hypnogram edition (see `Sleep examples <http://visbrain.org/auto_examples/index.html#sleep-examples>`_).
* :ref:`topo` : display topographical maps (see `Topo examples <http://visbrain.org/auto_examples/index.html#topoplot-examples>`_).
* :ref:`Ndviz` : visualize multidimensional data and basic plotting forms (see `Ndviz examples <http://visbrain.org/auto_examples/index.html#ndviz-examples>`_).
* :ref:`Figure` : figure-layout for high-quality publication-like figures (see `Figure examples <http://visbrain.org/auto_examples/index.html#figure-examples>`_).
* :ref:`colorbar` : colorbar editor (see `Colorbar examples <http://visbrain.org/auto_examples/index.html#colorbar-examples>`_).

See the :ref:`ChangelogFutur`.

Installation
************

Dependencies
============

Here's the list of visbrain's dependencies :

* Numpy
* Scipy
* Vispy : fast graphics rendering
* Matplotlib : mainly for colors and colormaps integration
* PyQt5 : Graphical User Interface components
* Pillow : for screenshots and image file format support.

We also strongly recommend to install *pyopengl* :

.. code-block:: shell

    pip install PyOpenGL PyOpenGL_accelerate

PyQt5 version
=============

For the PyQt5 version, Matplotlib's version should be >= 1.5.5. If PyQt is not installed, run either **pip install pyqt5** or **conda install pyqt**. Then, in a terminal run :

.. code-block:: shell

    pip install -e git+https://github.com/vispy/vispy#egg=vispy-dev

Finally, install Visbrain :

.. code-block:: shell

    pip install visbain

Develop mode
============

.. code-block:: shell

    git clone git@github.com:EtienneCmb/visbrain.git visbrain/
    cd visbrain/
    pip install -r requirements.txt
    python setup.py develop 


Contents:
*********

.. toctree::
   :maxdepth: 1

   community
   documentation
   auto_examples/index.rst
   changelog_futur


Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

