.. image:: https://travis-ci.org/EtienneCmb/visbrain.svg?branch=master
    :target: https://travis-ci.org/EtienneCmb/visbrain


Visbrain documentation
######################

Visbrain is a python package in development and it's dedicated to neuroscience visualization tools. Here is the list of the current modules :

* :ref:`brain` : plot your data onto a 3D MNI brain control it via the graphical interface
* :ref:`Sleep` : display sleep data, perform spindles / REM / peaks / slow waves / K-complex detection and live hypnogram edition
* :ref:`Ndviz` : inspect data your n-dimentional data.
* :ref:`Figure` : arange exported pictures in a grid, add colorbar and save a paper ready figure.

Installation
************

Here's the list of visbrain's dependancies :

* Numpy
* Scipy
* Vispy : fast graphics rendering
* Matplotlib : mainly for colors and colormaps integration
* PyQt4 : Graphical User Interface components
* Pillow : for screenshots and image file format support.

New Python versions (>= 3.6) and Matplotlib comes by default with PyQt5 and this a limitation because Visbrain use the GUI backends PyQt4. We are working to port Visbrain to PyQt5 but right now, you'll have to use a Python version under 3.6 and define an isolated environnement (ex : python=3.5). In addition, Visbrain use new VisPy functionalities and the most up-to-date VisPy version on PyPi is obsolete so you will have to install VisPy from Github.

First, in a terminal, create and activate a 3.5 Python environnement with the correct PyQt4 version :

.. code-block:: shell

    conda create --yes  -n visbrain python=3.5 numpy scipy pillow matplotlib=1.5.1 pip
    activate visbrain

Then you'll need to install the latest VisPy version from github :

.. code-block:: shell

    pip install -e git+https://github.com/vispy/vispy#egg=vispy-dev

Finally, install Visbrain :

.. code-block:: shell

    pip install visbain

What's new?
***********

* New in version v0.2.3

  * Sleep

    * New re-referencing method (common average)
    * Detection improvements
    * Add link to script and datasets to the doc

* New in version v0.2.2
  
  * Brain

    * Bug fixing

  * Sleep

    * Bug fixing
    * Save and load GUI configuration
    * Control the sleep stage order using the href input parameter
    * Enable/disable the drag and drop on load
    * Better Black and white hypnogram exportation
    * New shortcuts


Future plans
************

.. todo::
  
  * Visbrain

    * PyQt5 migration
    * pip and conda installation
  
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


Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

