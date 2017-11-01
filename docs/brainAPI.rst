
.. _BrainClass:

Main *Brain* class inputs
~~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: visbrain.brain.brain

.. autoclass:: Brain

    .. rubric:: Methods

    .. autosummary::
        ~Brain.show
        ~visbrain.brain.user.BrainUserMethods.rotate
        ~visbrain.brain.user.BrainUserMethods.background_color
        ~visbrain.brain.user.BrainUserMethods.screenshot
        ~visbrain.brain.user.BrainUserMethods.load_config
        ~visbrain.brain.user.BrainUserMethods.save_config

        ~visbrain.brain.user.BrainUserMethods.brain_control
        ~visbrain.brain.user.BrainUserMethods.brain_list
        ~visbrain.brain.user.BrainUserMethods.add_mesh

        ~visbrain.brain.user.BrainUserMethods.volume_control
        ~visbrain.brain.user.BrainUserMethods.add_volume
        ~visbrain.brain.user.BrainUserMethods.volume_list

        ~visbrain.brain.user.BrainUserMethods.cross_sections_control

        ~visbrain.brain.user.BrainUserMethods.sources_control
        ~visbrain.brain.user.BrainUserMethods.sources_display
        ~visbrain.brain.user.BrainUserMethods.sources_fit_to_vertices
        ~visbrain.brain.user.BrainUserMethods.sources_to_convex_hull

        ~visbrain.brain.user.BrainUserMethods.cortical_projection
        ~visbrain.brain.user.BrainUserMethods.cortical_repartition

        ~visbrain.brain.user.BrainUserMethods.time_series_control

        ~visbrain.brain.user.BrainUserMethods.pictures_control

        ~visbrain.brain.user.BrainUserMethods.connect_control

        ~visbrain.brain.user.BrainUserMethods.roi_control
        ~visbrain.brain.user.BrainUserMethods.roi_list

        ~visbrain.brain.user.BrainUserMethods.cbar_control
        ~visbrain.brain.user.BrainUserMethods.cbar_select
        ~visbrain.brain.user.BrainUserMethods.cbar_list
        ~visbrain.brain.user.BrainUserMethods.cbar_export
        ~visbrain.brain.user.BrainUserMethods.cbar_autoscale


.. ##########################################################################
..                                    GUI
.. ##########################################################################

GUI functions and settings
~~~~~~~~~~~~~~~~~~~~~~~~~~

Set of functions for an interactive control of the graphical user interface elements.

Show graphical interface
++++++++++++++++++++++++
.. automethod:: visbrain.pyqt_module.PyQtModule.show

Rotation
++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.rotate

Background color
++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.background_color

Screenshot
++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.screenshot

.. _LoadSaveConfig:

Load and save GUI configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Load an existing configuration
++++++++++++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.load_config

Save the current configuration
++++++++++++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.save_config

.. ##########################################################################
..                                    BRAIN
.. ##########################################################################

.. _BrainApi:

Brain methods
~~~~~~~~~~~~~

Set of functions for an interactive control of the main brain object. Use the methods below to define which brain template or hemisphere to display, the transparency level...

Control the brain
+++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.brain_control

List of available templates
+++++++++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.brain_list


Add mesh to the scene
+++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.add_mesh

.. ##########################################################################
..                       VOLUME AND CROSS-SECTIONS
.. ##########################################################################

.. _VolCrossecApi:

Volume and cross-sections
~~~~~~~~~~~~~~~~~~~~~~~~~

Control the volume
++++++++++++++++++

.. automethod:: visbrain.brain.user.BrainUserMethods.volume_control

Add volume
++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.add_volume

Get the list of volumes
+++++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.volume_list

Control cross-sections
++++++++++++++++++++++

.. automethod:: visbrain.brain.user.BrainUserMethods.cross_sections_control

.. ##########################################################################
..                                 SOURCES
.. ##########################################################################

.. _SourcesApi:

Sources methods
~~~~~~~~~~~~~~~

Set of functions for an interactive control of sources object. Use the methods below to pass some data to sources, to control the transparency level, to run the cortical projection / repartition...

Control sources
+++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.sources_control

Select sources
++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.sources_display

Fit to an object
++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.sources_fit_to_vertices

Convert into convex hull
++++++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.sources_to_convex_hull

.. _CortProj:

Cortical projection
+++++++++++++++++++

.. automethod:: visbrain.brain.user.BrainUserMethods.cortical_projection

.. _CortRepart:

Cortical repartition
++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.cortical_repartition

.. ##########################################################################
..                               TIME-SERIES
.. ##########################################################################

.. _TimeSeriesApi:

Time-series methods
~~~~~~~~~~~~~~~~~~~

Time-series control
+++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.time_series_control


.. ##########################################################################
..                                PICTURES
.. ##########################################################################

.. _PicturesApi:

Pictures methods
~~~~~~~~~~~~~~~~

Pictures control
++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.pictures_control

.. ##########################################################################
..                           CONNECTIVITY
.. ##########################################################################

.. _ConnectApi:

Connectivity methods
~~~~~~~~~~~~~~~~~~~~

Set of functions for an interactive control of connectivity object. Use the methods below to pass some data to connectivity, to control the transparency level...

Control Connectivity
++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.connect_control

.. ##########################################################################
..                                    ROI
.. ##########################################################################

.. _RoiApi:

Region Of Interest (ROI) methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set of functions for an interactive control of ROI (Region of interest) objects. Use methods below to select the ROI to display, to control the transparency level...

ROI control
+++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.roi_control

List of suported ROI
++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.roi_list

.. ##########################################################################
..                              COLORBAR
.. ##########################################################################

.. _CbarApi:

Colorbar methods
~~~~~~~~~~~~~~~~

Colorbar control
++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.cbar_control

Select a colorbar
+++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.cbar_select

List of available colorbars
+++++++++++++++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.cbar_list

Export colorbar
+++++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.cbar_export

Auto-scaling
++++++++++++
.. automethod:: visbrain.brain.user.BrainUserMethods.cbar_autoscale