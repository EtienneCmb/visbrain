.. _Release:

Changelog
=========

.. contents:: Contents
   :local:
   :depth: 1

0.4.6
-----

New features
~~~~~~~~~~~~

* Allow decoupling of the `scoring_window` and `display_window` to facilitate scoring of animal data in shorter epochs (`PR53 <https://github.com/EtienneCmb/visbrain/pull/53>`_)

0.4.5
-----

New features
~~~~~~~~~~~~

* Sulcus array support (`PR44 <https://github.com/EtienneCmb/visbrain/pull/44>`_)
* :class:`visbrain.objects.BrainObj` natively support Freesurfer files

Improvements
~~~~~~~~~~~~

* Update automatic detection of non-eeg channels used during re-referencing (`PR63 <https://github.com/EtienneCmb/visbrain/pull/63>`_)
* "Clean" channel labels only during bipolar re-referencing in Sleep (`PR63 <https://github.com/EtienneCmb/visbrain/pull/63>`_)
* Protect Sleep from MemoryError for large sleep files (`PR37 <https://github.com/EtienneCmb/visbrain/pull/37>`_)
* Improve spectrogram in case of non finite values (`PR39 <https://github.com/EtienneCmb/visbrain/pull/39>`_)
* Fix path to the url file for pyenv (`PR41 <https://github.com/EtienneCmb/visbrain/pull/41>`_)

Bug fixes
~~~~~~~~~
* Fix use of wrong channel during re-referencing to specific channel (`PR63 <https://github.com/EtienneCmb/visbrain/pull/63>`_)
* Fix `allow_pickle`
* Fix imresize from the scipy package

0.4.4
-----

New features
~~~~~~~~~~~~

* :class:`visbrain.objects.BrainObj` now support x3d, gii and obj files
* New object : :class:`visbrain.objects.GridSignalsObj` to plot multi-dimensional time-series and MNE instances or Raw, RawArray and Epochs
* Each object now inherits a method to animate it and to save the animation as a GIF. See for example :class:`visbrain.objects.BrainObj.animate` and :class:`visbrain.objects.BrainObj.record_animation`. Note that object can also be animate inside subplot (SceneObj)
* New object : :class:`visbrain.objects.VispyObj` makes VisPy's visuals compatibles with Visbrain's objects
* :class:`visbrain.objects.SourceObj` control masked sources' radius
* :class:`visbrain.objects.ConnectObj` finer control of transparency using input parameters `dynamic_order` and `dynamic_orientation`
* Objects and scenes can be plotted inside notebooks. For now it results in a non-interactive figure

Improvements
~~~~~~~~~~~~
* Make :class:`visbrain.objects` compatibles with `sphinx gallery <https://sphinx-gallery.readthedocs.io/en/latest/>`_
* Use scientific notation for colorbar extremas
* File extensions when loading sleep data (`PR32 <https://github.com/EtienneCmb/visbrain/pull/32>`_)
* Amplitude range of sleep files (`PR33 <https://github.com/EtienneCmb/visbrain/pull/33>`_)

Bug fixes
~~~~~~~~~
* Fix :class:`visbrain.gui.Signal` when using 1D signals

0.4.3
-----

New features
~~~~~~~~~~~~
* :class:`visbrain.objects.SourceObj.project_sources` can now be projected to a specific overlay.
* :class:`visbrain.objects.ConnectObj.get_nb_connections_per_node` to get the number of connections per node
* :class:`visbrain.objects.ConnectObj.analyse_connections` to analyse and group connectivity links per ROI
* :class:`visbrain.objects.RoiObj.get_centroids` to get the (x, y, z) MNI coordinates of ROIs' center

Improvements
~~~~~~~~~~~~
* Fix colormap update for every recording modality
* Colormap computed onto the GPU for : spectrogram, phase-amplitude coupling, images, 3D images, brain object, grid signals
* Sorted brain templates in :class:`visbrain.Brain` + remove sulcus as a brain template
* Fewer visible possibilities when importing from the root of visbrain 
* Remove all data from the visbrain package
* Include MIST ROI template to the :class:`visbrain.objects.RoiObj`
* Enable to filter ROIs from the Brain GUI

Bug fixes
~~~~~~~~~
* Brain scaling in :class:`visbrain.mne.mne_plot_source_estimation`
* Recursive folder creation for brain template
* Select from the GUI brain template build with vertices and faces
* Repeat source localization using the same RoiObj
* Colorbar module has been removed and replaced by CbarObj
* Insert annotation inside Signal
* Smoothing for MEG data (`PR20 <https://github.com/EtienneCmb/visbrain/pull/20>`_)

0.4.1
-----

New features
~~~~~~~~~~~~

* You can now :ref:`replace_detection` using the :class:`visbrain.Sleep.replace_detections` method.
* Add activations (:class:`visbrain.objects.CrossSecObj.set_activation`) and highlight multiple sources (:class:`visbrain.objects.CrossSecObj.highlight_sources`) inside the :class:`visbrain.objects.CrossSecObj`
* Plot MNE sources :class:`visbrain.mne.mne_plot_source_space`


Improvements
~~~~~~~~~~~~

* :class:`visbrain.objects.CrossSecObj` : much faster + colormap computed onto the GPU + superposition of multiple mask + keyboard interactions

Bug fixes
~~~~~~~~~

* :class:`visbrain.objects.BrainObj.parcellize` using nibabel >= 2.3
* colorbar control of :class:`visbrain.objects.Picture3DObj` object
* add multiple objects to the :class:`visbrain.objects.SceneObj` with *row_span* and / or *col_span* > 1 
* path to brain templates
* loading hypnogram with spaces instead of tabs
* Fix :class:`visbrain.mne.mne_plot_source_estimation` with left and right hemispheres
* Fix activations that disappear using :class:`visbrain.Brain.brain_control`
* Fix x and y axis update inside :class:`visbrain.Signal`
* Reading Nifti files with NaN values

0.4.0
-----

New features
~~~~~~~~~~~~

* Plot MNE estimated sources :class:`visbrain.mne.mne_plot_source_estimation`

Improvements
~~~~~~~~~~~~

* JSON saving for configuration file

Bug fixes
~~~~~~~~~

* visbrain installation (no requirements file)
* compatibility with numpy and pip
* broken examples + templates/ folder
* Hypnogram is now exported as a .txt file with stage-duration encoding.
* .xlsx and EDF+ are now supported for hypnogram
* units when loading with MNE
* warning in UTF-8 file loading
* compatibility with numpy and pip


0.3.8
-----


New features
~~~~~~~~~~~~

* Multitaper-based spectrogram (require `lspopt <https://github.com/hbldh/lspopt>`_ package, see doc) 

Improvements
~~~~~~~~~~~~

* Added logging
* Code improvements: PEP8 and flake8
* automatic spindles detection
* Simplified and improved Sleep GUI
* Removed drag-and-drop method for hypnogram scoring
