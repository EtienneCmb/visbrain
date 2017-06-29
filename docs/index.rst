.. image:: https://travis-ci.org/EtienneCmb/visbrain.svg?branch=master
    :target: https://travis-ci.org/EtienneCmb/visbrain

.. image:: https://codecov.io/gh/EtienneCmb/visbrain/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/EtienneCmb/visbrain

.. image:: https://badge.fury.io/py/visbrain.svg
  :target: https://badge.fury.io/py/visbrain


Visbrain documentation
######################

Visbrain is a python package dedicated to multi-purpose neuroscience visualization tools. Here is the list of the current modules :

* :ref:`brain` : plot your data onto a 3D MNI brain control it via the graphical interface
* :ref:`Sleep` : display sleep data, perform spindles / REM / peaks / slow waves / K-complex detection and live hypnogram edition
* :ref:`Ndviz` : inspect data your n-dimentional data.
* :ref:`Figure` : arange exported pictures in a grid, add colorbar and save a paper ready figure.

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

Since the 0.2.8 Visbrain use the PyQt5 version. If you still use PyQt4, you should install the Visbrain version 0.2.7.

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

What's new?
***********

* New in version v0.2.9
  
  * Visbrain

    * Better integration of PyQt5
    * Start grouping read/write function in I/O
  
  * Brain

    * New menu and much cleaner code and GUI
    * New colorbar
    * **Shortcuts has changed**
    * You can now save/load the GUI configuration either from the menu File/load or File/save or using methods *loadConfig* and *saveConfig* 

  * Sleep

    * Support annotations
    * Enable editing/removing detections
    * Improve default topoplot state


* New in version v0.2.8

  * Visbrain

    * Migration to PyQt5
    * Start new module *Colorbar* for a better integration of color controls and properties.

  * Sleep

    * Enable exporting colored hypnogram
    * Bug fixing & GUI improvements

* New in version v0.2.3

  * Sleep

    * New re-referencing method (common average)
    * Detection improvements
    * Add link to script and datasets to the doc


Future plans
************

.. todo::
  
  * Visbrain

    * conda installation
  
  * Brain

    * Compatibility with other brain templates
    * Display brain signals/2D maps attached to sources
    * Better integration of ROI + possibility to the user to use other volume templates

  * Sleep

    * Improve detections GUI integration
    * Add default supported files integration
    * Color screenshot
    * Command line control
    * Automatic scoring


Contents:
*********

.. toctree::
   :maxdepth: 3

   brain
   sleep
   ndviz
   figure
   io


Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

