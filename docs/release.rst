.. _Release:

Changelog
---------

Version 0.4.1
=============

Brain
~~~~~
* Fix path to brain templates

Sleep
~~~~~
* Fix loading hypnogram with spaces instead of tabs

Version 0.4.0
=============

Visbrain
~~~~~~~~
* Fixed installation
* Fixed compatibility with numpy and pip

Brain
~~~~~
* **[NEW]** `mne_plot_source_estimation <https://github.com/EtienneCmb/visbrain/blob/master/visbrain/mne/plot_fwd.py>`_
* Fixed broken examples + templates/ folder

Sleep
~~~~~
* **[NEW]** Hypnogram is now exported as a .txt file with stage-duration encoding.
* **[NEW]** .xlsx and EDF+ are now supported for hypnogram
* Fixed units when loading with MNE
* Fixed warning in UTF-8 file loading
* Improved JSON saving for configuration file
* Fixed compatibility with numpy and pip

Version 0.3.8
=============

Visbrain
~~~~~~~~

* Added logging
* Code improvements: PEP8 and flake8

Sleep
~~~~~

* Simplified and improved user interface
* Multitaper-based spectrogram (require `lspopt <https://github.com/hbldh/lspopt>`_ package, see doc)
* Improved automatic spindles detection
* Removed drag-and-drop method for hypnogram scoring
