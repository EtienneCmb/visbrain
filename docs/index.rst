Visbrain documentation
######################

Visbrain is a python package in development and it's dedicated to neuroscience visualization tools. Here is the list of the current modules :

* :ref:`brain` : plot your data onto a 3D MNI brain control it via the graphical interface
* :ref:`Sleep` : display sleep data, perform spindles / REM / peaks / slow waves / K-complex detection and live hypnogram edition
* :ref:`Ndviz` : inspect data your n-dimentional data.
* :ref:`Figure` : arange exported pictures in a grid, add colorbar and save a paper ready figure.

Installation:
*************

First, visbrain use PyQt4 which means that you need to use a python version under 3.5.2. The same for the matplotlib version (<= 1.5.1). Then you need to install VisPy, which is a Python library for interactive scientific visualization. In order to install this package's dependencies (OpenGL), checkout this `installation guide <http://vispy.org/installation.html>`_. You'll need to install the developper version of VisPy. Run the following code in a terminal :

Clone visbrain repository :

.. code-block:: bash

    git clone https://github.com/EtienneCmb/visbrain.git

Go to the cloned folder and run :

.. code-block:: bash

    pip install .

What's new?
***********

* New in version v0.2.1

  * Brain

    * New *add_mesh*, *sources_fit* and *sources_to_convexHull* methods
    * Improve projection on selected objects

  * Sleep

    * Load .trc files (Micromed)
    * New *Muscle twiches* detection
    * Dections improvements and better GUI integrations
    * Import / export all detections for latter use
    * Fix detections after bipolarization
    * New shortcuts

* New in version v0.2.0

  * Brain : new *ui_autocrop* parameter (or using the *screenshot* function)
  * Figure : new `example <https://github.com/EtienneCmb/visbrain/tree/master/examples/figure>`_
  * Figure : new *autocrop* parameter for automatic size ajustments and doc update
  * Sleep : doc updates and python 2 bug fixing.

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

