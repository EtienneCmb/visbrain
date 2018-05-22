.. _ChangelogFutur:

Changelog and future directions
###############################

v0.4.0
^^^^^^

Visbrain
~~~~~~~~
* Fixed installation #15 
* Fixed compatibility with numpy and pip

Brain
~~~~~
* **[NEW]** [mne_plot_source_estimation](https://github.com/EtienneCmb/visbrain/blob/master/visbrain/mne/plot_fwd.py)
* Fixed broken examples + templates/ folder

Sleep
~~~~~
* **[NEW]** Hypnogram is now exported as a .txt file with stage-duration encoding.
* **[NEW]** .xlsx and EDF+ are now supported for hypnogram
* Fixed units when loading with MNE
* Fixed warning in UTF-8 file loading
* Improved JSON saving for configuration file
* Fixed compatibility with numpy and pip

v0.3.8
^^^^^^

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
