.. _Release:

Changelog
---------

Version 0.4.1
=============

Visbrain
~~~~~~~~
* **[FIX]** add multiple objects to scene with *row_span* and / or *col_span* > 1

Brain
~~~~~
* **[FIX]** path to brain templates

Sleep
~~~~~
* **[FIX]** loading hypnogram with spaces instead of tabs

Version 0.4.0
=============

Visbrain
~~~~~~~~
* **[FIX]** installation
* **[FIX]** compatibility with numpy and pip

Brain
~~~~~
* **[NEW]** `mne_plot_source_estimation <https://github.com/EtienneCmb/visbrain/blob/master/visbrain/mne/plot_fwd.py>`_
* **[FIX]** broken examples + templates/ folder

Sleep
~~~~~
* **[NEW]** Hypnogram is now exported as a .txt file with stage-duration encoding.
* **[NEW]** .xlsx and EDF+ are now supported for hypnogram
* **[FIX]** units when loading with MNE
* **[FIX]** warning in UTF-8 file loading
* Improved JSON saving for configuration file
* **[FIX]** compatibility with numpy and pip

Version 0.3.8
=============

Visbrain
~~~~~~~~

* Added logging
* Code improvements: PEP8 and flake8

Sleep
~~~~~

* Simplified and improved user interface
* **[NEW]** Multitaper-based spectrogram (require `lspopt <https://github.com/hbldh/lspopt>`_ package, see doc)
* Improved automatic spindles detection
* Removed drag-and-drop method for hypnogram scoring
