
Main *Brain* class inputs
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: visbrain.brain.brain.Brain


*Brain* methods
~~~~~~~~~~~~~~~

The functions below are subdivided into several parts :

* GUI functions : control the graphical user interface (display, rotation, screenshot...)
* Brain functions : control the main brain object (color, transparency...)
* Sources functions : control sources object (color, transparency, data...)
* Connectivity functions : control connectivity object (color, transparency, data...)
* ROI functions : control ROI object (selected areas, color, transparency...)

GUI functions and settings
^^^^^^^^^^^^^^^^^^^^^^^^^^

Set of functions for an interactive control of the graphical user interface elements. 

Show graphical interface
++++++++++++++++++++++++
.. automethod:: visbrain.brain.brain.Brain.show

Quit graphical interface
++++++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.quit

Rotation
++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.rotate

Background color
++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.background_color

Screenshot
++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.screenshot

Load and save GUI configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Load an existing configuration
++++++++++++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.load_config

Save the current configuration
++++++++++++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.save_config

Atlas methods
^^^^^^^^^^^^^

Set of functions for an interactive control of the main brain object. Use the methods below to define which brain template or hemisphere to display, the transparency level...

.. figure::  picture/BrainObj.png
   :align:   center

   Several brain templates and control possiblities.

Control
+++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.brain_control

Opacity
+++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.brain_opacity


Light reflection
++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.light_reflection


Sources methods
^^^^^^^^^^^^^^^

Set of functions for an interactive control of sources object. Use the methods below to pass some data to sources, to control the transparency level, to run the cortical projection / repartition...

.. figure::  picture/SourcesObj.png
   :align:   center

Source's settings
+++++++++++++++++

.. automethod:: visbrain.brain.user.BrainUserMethods.sources_settings

Opacity
+++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.sources_opacity

.. figure::  picture/ProjObj.png
   :align:   center

   Example of cortical projection.

Select sources
++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.sources_display

Add source object
+++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.add_sources

Fit to an object
++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.sources_fit

Convert into convex hull
++++++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.sources_to_convex_hull

Cortical projection
+++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.cortical_projection

Cortical repartition
++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.cortical_repartition

Colormap
++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.sources_colormap


Time-series methods
^^^^^^^^^^^^^^^^^^^

Time-series settings
++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.time_series_settings


Add time-series
+++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.add_time_series

Pictures methods
^^^^^^^^^^^^^^^^

Pictures settings
+++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.pictures_settings


Add pictures
++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.add_pictures

Connectivity methods
^^^^^^^^^^^^^^^^^^^^

Set of functions for an interactive control of connectivity object. Use the methods below to pass some data to connectivity, to control the transparency level...

.. figure::  picture/ConnectObj.png
   :align:   center

   Example of connectivity setup.

Connectivity settings
+++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.connect_settings

Add connectivity object
+++++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.add_connect

ROI methods
^^^^^^^^^^^

Set of functions for an interactive control of ROI (Region of interest) objects. Use methods below to select the ROI to display, to control the transparency level...

.. figure::  picture/AreaObj.png
   :align:   center

   Example of deep-structures (AAL / Brodmann area).

List of suported ROI
++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.roi_list

Plot selection
++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.roi_plot

Opacity
+++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.roi_opacity

Light reflection
++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.roi_light_reflection

Colorbar methods
^^^^^^^^^^^^^^^^

Colorbar control
++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.cbar_control

Auto-scaling
++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.cbar_autoscale