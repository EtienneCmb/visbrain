Visbrain documentation
######################

Visbrain is a python package in development and it's dedicated to neuroscience visualization tools. Here is the list of the current modules :

* :ref:`vbrain` : plot your data onto a 3D MNI brain control it via the graphical interface
* :ref:`Ndviz` : inspect data your n-dimentional data.
* :ref:`vbmakefig` : concatenate several pictures

Installation:
*************

First, the vbrain module use PyQt4 which means that you need to use a python version under 3.5.2. The same for the matplotlib version (<= 1.5.1). Then you need to install VisPy, which is a Python library for interactive scientific visualization. In order to install this package's dependencies (OpenGL), checkout this `installation guide <http://vispy.org/installation.html>`_. You'll need to install the developper version of VisPy. Run the following code in a terminal :

.. code-block:: python

    pip install -e git+https://github.com/vispy/vispy#egg=vispy-dev

Finally, install visbrain :

.. code-block:: python

    pip install git+https://github.com/EtienneCmb/visbrain

What's new?
***********
New in version v0.0.3:

* New documentation
* Code cleaned
* File and folder structure changed
* New user functions : control the interface without to opening it
* Improve colormap / colorbar managment
* Bug fixed

Contents:
*********

.. toctree::
   :maxdepth: 3
   
   vbrain
   ndviz


Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

