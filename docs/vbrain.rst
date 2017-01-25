.. _vbrain:

vbrain
######

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

Show graphical interface
~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: vbrain.vbrain.vbrain.show

Brain control
~~~~~~~~~~~~~~
.. automethod:: vbrain.interface.uiElements.uiAtlas.uiAtlas.brain_control

Brain rotation
~~~~~~~~~~~~~~
.. automethod:: vbrain.interface.uiElements.uiAtlas.uiAtlas.rotate

Brain structure
~~~~~~~~~~~~~~
.. automethod:: vbrain.interface.uiElements.uiAtlas.uiAtlas.brain_structure

Cortical projection
~~~~~~~~~~~~~~~~~~~
.. automethod:: vbrain.elements.transformations.SourcesTransform.SourcesTransform.cortical_projection

Cortical repartition
~~~~~~~~~~~~~~~~~~~~
.. automethod:: vbrain.elements.transformations.SourcesTransform.SourcesTransform.cortical_repartition
