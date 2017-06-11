Visbrain documentation
######################

Visbrain is a python package in development and it's dedicated to neuroscience visualization tools. Here is the list of the current modules :

* :ref:`brain` : plot your data onto a 3D MNI brain control it via the graphical interface
* :ref:`Sleep` : display sleep data, perform spindles / REM / peaks / slow waves / K-complex detection and live hypnogram edition
* :ref:`Ndviz` : inspect data your n-dimentional data.
* :ref:`Figure` : arange exported pictures in a grid, add colorbar and save a paper ready figure.

Installation:
*************

First, visbrain use PyQt4 which means that you need to use a python version under 3.5.2. The same for the matplotlib version (<= 1.5.1). Then you need to install VisPy, which is a Python library for interactive scientific visualization. In order to install this package's dependencies (OpenGL), checkout this `installation guide <http://vispy.org/installation.html>`_. You'll need to install the developper version of VisPy.

Environnement configuration and visbrain installation on windows and python 3 :

.. code-block:: bash

    conda create --yes -n visbrain python=3.5 anaconda
    activate visbrain
    git clone https://github.com/EtienneCmb/visbrain.git visbrain
    git clone https://github.com/vispy/vispy vispy
    cd vispy
    python setup.py install
    cd ..\visbrain
    pip install . --no-deps
    conda install --yes pyqt=4

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

