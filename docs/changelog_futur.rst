.. _ChangelogFutur:

Changelog and future directions
###############################

Changelog
---------

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

v0.3.4
^^^^^^

Visbrain
~~~~~~~~

* *Ndviz* has been replaced by *Signal*

Sleep
~~~~~

* List of supported files has been extended + better integration of MNE
* Start lazy loading for huge files
* Improve down-sampling
* Command-line control

Future directions
-----------------

Visbrain
^^^^^^^^

* Conda installation
* New modules are planned (*Connect*, *Pictures*, *ERP*) (LT)

Brain
^^^^^

* Colorbar support very low and very high values (see utils.power_of_ten) (ST)
* Better ROI color control (ST)
* Support load atlas from several extensions (LT)
* Support adding custom ROI (LT)

Sleep
^^^^^

* De-noising (LT)
* Zero re-referencing (LT)
* Automatic-scoring (LT)

Figure
^^^^^^

* Improve memory efficiency when loading files in a loop.
