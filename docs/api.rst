.. _API:


API
===

.. contents::
   :local:
   :depth: 2


Graphical user interface
------------------------

:py:mod:`visbrain.gui`:

.. currentmodule:: visbrain.gui

.. automodule:: visbrain.gui
   :no-members:
   :no-inherited-members:


.. autosummary::
   :toctree: generated/
   :template: qt_class.rst

   Brain
   Sleep
   Signal
   Figure


Objects
-------

:py:mod:`visbrain.objects`:

.. currentmodule:: visbrain.objects

.. automodule:: visbrain.objects
   :no-members:
   :no-inherited-members:

.. autosummary::
   :toctree: generated/
   :template: obj_class.rst

    BrainObj
    ColorbarObj
    ConnectObj
    CrossSecObj
    GridSignalsObj
    HypnogramObj
    ImageObj
    PacmapObj
    Picture3DObj
    RoiObj
    SceneObj
    SourceObj
    TopoObj
    TimeFrequencyObj
    TimeSeries3DObj
    VectorObj
    VispyObj
    VolumeObj

Compatibility with existing software
------------------------------------

MNE-python
~~~~~~~~~~

:py:mod:`visbrain.mne`:

.. currentmodule:: visbrain.mne

.. automodule:: visbrain.mne
   :no-members:
   :no-inherited-members:

.. autosummary::
   :toctree: generated/
   :template: function.rst

   mne_plot_source_estimation
   mne_plot_source_space

I/O
---

:py:mod:`visbrain.io`:

.. currentmodule:: visbrain.io

.. automodule:: visbrain.io
   :no-members:
   :no-inherited-members:

.. autosummary::
   :toctree: generated/
   :template: function.rst

   download_file
   path_to_visbrain_data
   read_stc
   write_fig_hyp
   get_sleep_stats

Miscellaneous
-------------

:py:mod:`visbrain.utils`:

.. currentmodule:: visbrain.utils

.. automodule:: visbrain.utils
   :no-members:
   :no-inherited-members:

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

.. currentmodule:: visbrain.utils

.. autosummary::
   :toctree: generated/

    Colormap
