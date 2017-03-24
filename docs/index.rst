Visbrain documentation
######################

Visbrain is a python package in development and it's dedicated to neuroscience visualization tools. Here is the list of the current modules :

* :ref:`brain` : plot your data onto a 3D MNI brain control it via the graphical interface
* :ref:`Sleep` : display sleep data, perform spindles / REM / peaks / slow waves / K-complex detection and live hypnogram edition
* :ref:`Ndviz` : inspect data your n-dimentional data.
* :ref:`makefig` : concatenate several pictures

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

* New in version v0.1.8

  * Brain : New density color and start bundling
  * Brain : possibility to add multiple source / connectivity objects
  * Brain : screenshot improvements and GUI integration
  * Sleep : new slow wave / K-complex detection
  * Sleep : REM / spindles detection improvements
  * Sleep : everything can now be exported.
  * Sleep : GUI re-organization and improvements

* New in version v0.1.4

  * Python 2 compatibility
  * Sleep module and doc improvements

* New in version v0.1.2

  * vbrain has been renamed to Brain()
  * exportation improvements
  * New screenshot tutorial

Contents:
*********

.. toctree::
   :maxdepth: 3
   
   brain
   sleep
   ndviz
   makefig


Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

