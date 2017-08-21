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

Visbrain is a python package dedicated to multi-purpose neuroscience visualization tools. Here is the list of the current modules :

* :ref:`brain` : plot your data onto a 3D MNI brain control it via the graphical interface
* :ref:`colorbar` : design a colorbar
* :ref:`Figure` : arange exported pictures in a grid, add colorbar and save a paper ready figure.
* :ref:`Ndviz` : inspect data your n-dimentional data.
* :ref:`Sleep` : display sleep data, perform spindles / REM / peaks / slow waves / K-complex detection and live hypnogram edition
* :ref:`topo` : topographic representations

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

    pip install pyopengl

PyQt5 version
=============

For the PyQt5 version, Matplotlib's version should be >= 1.5.5. If PyQt is not installed, run either **pip install pyqt5** or **conda install pyqt**. Then, in a terminal run :

.. code-block:: shell

    pip install -e git+https://github.com/vispy/vispy#egg=vispy-dev

Finally, install Visbrain :

.. code-block:: shell

    pip install visbain

PyQt4 version
=============

Since version 0.2.8, Visbrain use the PyQt5. If you still use PyQt4, you should install the Visbrain version 0.2.7.

In a terminal, create and activate a 3.5 Python environment with the correct PyQt4 version :

.. code-block:: shell

    conda create --yes  -n visbrain python=3.5 numpy scipy pillow matplotlib=1.5.1 pip
    activate visbrain

Then you'll need to install the latest VisPy version from github :

.. code-block:: shell

    pip install -e git+https://github.com/vispy/vispy#egg=vispy-dev

Finally, install Visbrain :

.. code-block:: shell

    pip install visbain==0.2.7


Contents:
*********

.. toctree::
   :maxdepth: 3

   brain
   colorbar
   figure
   ndviz
   sleep
   topo
   utils
   io
   auto_examples/index.rst
   changelog_futur


Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

