.. _vbrain:

vbrain
======

Description
-----------

.. figure::  picture/example.png
   :align:   center

Vbrain is a flexible graphical user interface for 3D visualizations on an MNI brain. It can be use to display deep sources, brodmann areas, materialize connectivity... This module use `vispy <http://vispy.org/>`_ and can be imported as follow :

.. code-block:: python

    from visbrain import vbrain

All possible inputs use a prefixe :

	* 'a(_)': atlas properties
	* 's(_)': sources properties
	* 'c(_)': connectivity properties
	* 'cmap(_)': colormap properties
	* 't(_)': transformations properties
	* 'ui(_)': graphical interface properties
	* 'cb(_)': colorbar properties
	* 'l(_)': light properties

.. autoclass:: vbrain.vbrain.vbrain

User functions
--------------

.. toctree::
   :maxdepth: 4
   
   vbfunctions