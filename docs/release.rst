.. _Release:

Changelog
=========

.. contents:: Contents
   :local:
   :depth: 1

0.4.1
-----

New features
~~~~~~~~~~~~

Bug fixes
~~~~~~~~~

* colorbar control of Picture3DObj object
* add multiple objects to scene with *row_span* and / or *col_span* > 1 
* path to brain templates
* loading hypnogram with spaces instead of tabs

0.4.0
-----

New features
~~~~~~~~~~~~

* `mne_plot_source_estimation <https://github.com/EtienneCmb/visbrain/blob/master/visbrain/mne/plot_fwd.py>`_ 

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
