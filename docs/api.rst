.. _API:


API
===

.. contents::
   :local:
   :depth: 2


GUI based modules
-----------------

.. currentmodule:: visbrain

.. autosummary::
   :toctree: generated/
   :template: qt_class.rst

   Brain
   Sleep
   Topo
   Signal
   Figure


.. _API_objects:


Objects
-------

.. currentmodule:: visbrain.objects

.. autosummary::
   :toctree: generated/
   :template: obj_class.rst

    BrainObj
    ColorbarObj
    ConnectObj
    CrossSecObj
    HypnogramObj
    ImageObj
    Picture3DObj
    RoiObj
    SceneObj
    SourceObj
    TimeFrequencyObj
    TimeSeries3DObj
    VectorObj
    VolumeObj

Compatibility with existing software
------------------------------------

.. currentmodule:: visbrain.mne

.. autosummary::
   :toctree: generated/
   :template: function.rst

   mne_plot_source_estimation

I/O
---

.. currentmodule:: visbrain.io

.. autosummary::
   :toctree: generated/
   :template: function.rst

   download_file
   path_to_visbrain_data
   read_stc

Miscellaneous
-------------

.. currentmodule:: visbrain.utils

.. autosummary::
   :toctree: generated/
   :template: function.rst

   generate_eeg
   tal2mni
   mni2tal
   rereferencing
   bipolarization
   commonaverage
   convert_meshdata
   volume_to_mesh
   color2vb
   array2colormap

Command line
------------

In addition to using Python script, you can also use the following command-lines from a terminal :

* :ref:`cli_visbrain_sleep` : open the graphical user interface of Sleep.
* :ref:`cli_visbrain_fig_hyp` : export a hypnogram file (**.txt**, **.csv** or **.hyp**) into a high definition colored or black and white image.
* :ref:`cli_visbrain_sleep_stats` : Compute sleep statistics from hypnogram file and export them in csv.

.. _cli_visbrain_sleep:
.. click:: visbrain.cli:cli_sleep
   :prog: visbrain_sleep

.. _cli_visbrain_fig_hyp:
.. click:: visbrain.cli:cli_fig_hyp
   :prog: visbrain_fig_hyp

.. _cli_visbrain_sleep_stats:
.. click:: visbrain.cli:cli_sleep_stats
   :prog: visbrain_sleep_stats
