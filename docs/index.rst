Visbrain documentation
######################

Visbrain is a python package in development and it's dedicated to neuroscience visualization tools. Here is the list of the current modules :

* :ref:`vbrain` : plot your data onto a 3D MNI brain control it via the graphical interface
* :ref:`Sleep` : display sleep data, perform spindles / REM / peaks detection and live hypnogram edition
* :ref:`Ndviz` : inspect data your n-dimentional data.
* :ref:`makefig` : concatenate several pictures

Installation:
*************

First, the vbrain module use PyQt4 which means that you need to use a python version under 3.5.2. The same for the matplotlib version (<= 1.5.1). Then you need to install VisPy, which is a Python library for interactive scientific visualization. In order to install this package's dependencies (OpenGL), checkout this `installation guide <http://vispy.org/installation.html>`_. You'll need to install the developper version of VisPy. Run the following code in a terminal :

Clone visbrain repository :

.. code-block:: bash

    git clone https://github.com/EtienneCmb/visbrain.git

Finally, install visbrain :

.. code-block:: python

    python setup.py install

What's new?
***********

* New in version v0.1.0:
	* vbrain GUI improvements (design, source's panel and ROI)
	* better control of ROI
* New in version v0.1.0:
	* New module :ref:`Sleep`
* New in version v0.0.4:
	* New module :ref:`Ndviz`

Contents:
*********

.. toctree::
   :maxdepth: 3
   
   vbrain
   sleep
   ndviz
   makefig


Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

