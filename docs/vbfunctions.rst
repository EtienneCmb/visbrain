The functions below are subdivided into several parts :

* GUI functions : control the graphical user interface (display, rotation, screenshot...)
* Brain functions: control the main brain object (color, transparency...)
* Sources functions: control sources object (color, transparency, data...)
* Connectivity functions: control connectivity object (color, transparency, data...)
* ROI functions: control area object (selected areas, color, transparency...)

GUI functions and settings
^^^^^^^^^^^^^^^^^^^^^^^^^^

Set of functions for an iteractive control of the graphical user interface elements. 

Show graphical interface
~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.brain.Brain.show

Quit graphical interface
~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.quit

Rotation
~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.rotate

Background color
~~~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.background_color

Screenshot
~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.screenshot

Brain functions
^^^^^^^^^^^^^^^

Set of functions for an iteractive control of the main brain object. Use the methods below to define which brain template or hemisphere to display, the transparency level...

.. figure::  picture/BrainObj.png
   :align:   center

   Several brain templates and control possiblities.

Control
~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.brain_control

Opacity
~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.brain_opacity


Light reflection
~~~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.light_reflection


Sources functions
^^^^^^^^^^^^^^^^^

Set of functions for an iteractive control of sources object. Use the methods below to pass some data to sources, to control the transparency level, to run the cortical projection / repartition...

.. figure::  picture/SourcesObj.png
   :align:   center

Set data
~~~~~~~~

.. automethod:: visbrain.brain.user.userfcn.sources_data

Opacity
~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.sources_opacity

.. figure::  picture/ProjObj.png
   :align:   center

   Example of cortical projection.

Select sources
~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.sources_display

Add source object
~~~~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.add_sources

Fit to an object
~~~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.sources_fit

Convert into convex hull
~~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.sources_to_convexHull

Cortical projection
~~~~~~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.cortical_projection

Cortical repartition
~~~~~~~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.cortical_repartition

Colormap
~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.sources_colormap

Connectivity functions
^^^^^^^^^^^^^^^^^^^^^^

Set of functions for an iteractive control of connectivity object. Use the methods below to pass some data to connectivity, to control the transparency level...

.. figure::  picture/ConnectObj.png
   :align:   center

   Example of connectivity setup.

Connectivity settings
~~~~~~~~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.connect_display

Add connectivity object
~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.add_connect

ROI functions
^^^^^^^^^^^^^

Set of functions for an iteractive control of ROI (Region of interest) objects. Use methods below to select the ROI to display, to control the transparency level...

.. figure::  picture/AreaObj.png
   :align:   center

   Example of deep-structures (AAL / Brodmann area).

List of suported ROI
~~~~~~~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.roi_list

Plot selection
~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.roi_plot

Opacity
~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.roi_opacity

Light reflection
~~~~~~~~~~~~~~~~
.. automethod:: visbrain.brain.user.userfcn.roi_light_reflection
