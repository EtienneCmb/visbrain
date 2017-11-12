.. image:: https://travis-ci.org/EtienneCmb/visbrain.svg?branch=master
    :target: https://travis-ci.org/EtienneCmb/visbrain

.. image:: https://ci.appveyor.com/api/projects/status/fdxhhmpagms1so8l?svg=true
    :target: https://ci.appveyor.com/project/EtienneCmb/visbrain/branch/master

.. image:: https://circleci.com/gh/EtienneCmb/visbrain/tree/master.svg?style=svg
    :target: https://circleci.com/gh/EtienneCmb/visbrain/tree/master

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

Visbrain is an open-source python 3 package dedicated to brain signals visualization. It is based on top of VisPy and PyQt and is distributed under the 3-Clause BSD license.

.. figure::  /picture/visbrain_readme.png
   :align:   center

Visbrain includes six visualization modules :

* :ref:`BrainModule` : visualize EEG/MEG/Intracranial data, connectivity in a standard MNI 3D brain (see `Brain examples <http://visbrain.org/auto_examples/index.html#brain-examples>`_).
* :ref:`Sleep` : visualize polysomnographic data and hypnogram edition (see `Sleep examples <http://visbrain.org/auto_examples/index.html#sleep-examples>`_).
* :ref:`Signal` : data-mining module for time-series inspection (see `Signal examples <http://visbrain.org/auto_examples/index.html#signal-examples>`_).
* :ref:`Topo` : display topographical maps (see `Topo examples <http://visbrain.org/auto_examples/index.html#topoplot-examples>`_).
* :ref:`Figure` : figure-layout for high-quality publication-like figures (see `Figure examples <http://visbrain.org/auto_examples/index.html#figure-examples>`_).
* :ref:`colorbar` : colorbar editor (see `Colorbar examples <http://visbrain.org/auto_examples/index.html#colorbar-examples>`_).

See the :ref:`ChangelogFutur`.

Installation
************

Dependencies
============

Here's the list of visbrain's dependencies :

* Numpy (>= 1.13)
* Scipy
* Vispy (>= 0.5.0) : fast graphics rendering
* Matplotlib (>= 1.5.5): mainly for colors and colormaps integration
* PyQt5 : Graphical User Interface components
* Pillow : for screenshots and image file format support.

We also strongly recommend to install *pandas* and *pyopengl* :

.. code-block:: shell

    pip install pandas PyOpenGL PyOpenGL_accelerate

Installation
============

For the PyQt5 version, Matplotlib's version should be >= 1.5.5. If PyQt is not installed, run either **pip install pyqt5** or **conda install pyqt**. Then, in a terminal run :

Install Visbrain :

.. code-block:: shell

    pip install visbrain

Develop mode
============

.. code-block:: shell

    git clone https://github.com/EtienneCmb/visbrain.git visbrain/
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

