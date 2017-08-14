.. _ChangelogFutur:

Changelog and future directions
###############################

Changelog
---------

v0.3.0
^^^^^^

Brain module
~~~~~~~~~~~~

* Add time-series and pictures attached to sources
* Colorbar integration improvements
* Add volume and cross-sections
* Enable to import new brain template and nifti volumes
* Add XYZ source's tab to find where source's are localized
* Improve ROI selection
* New user methods
* GUI and Doc improvements

v0.2.9
^^^^^^

Visbrain
~~~~~~~~

* Better integration of PyQt5
* Start grouping read/write function in I/O
* Fix closing window when Python error occurs

Brain module
~~~~~~~~~~~~

* New menu and much cleaner code and GUI
* New colorbar with better controls
* **Shortcuts has changed**
* Save/load the GUI configuration either from the menu File/load or File/save or using methods *loadConfig* and *saveConfig*
* Fix camera

Sleep module
~~~~~~~~~~~~

* Support annotations
* Enable editing/removing detections
* Improve default topoplot state

Colorbar module
~~~~~~~~~~~~~~~

* **New colorbar module** : use this new module to design colorbars and to export the configuration.

v0.2.8
^^^^^^

Visbrain
~~~~~~~~

* Migration to PyQt5

Sleep module
~~~~~~~~~~~~

* Enable exporting colored hypnogram
* Bug fixing & GUI improvements


Future directions
-----------------

Visbrain
^^^^^^^^

* conda installation
* Independent of the VisPy developer version for better installation (ST)
* Code style improvements (flake8 and numpydoc) (ST)
* Improve coverage (right now, PyQt tests failed) (ST)
* Improve doc with sphinx-gallery (ST)
* New modules are planned (*Connect*, *Signal*, *Image*, *ERP*, *Topo*) (LT)

Brain
^^^^^

* Colorbar support very low and very high values (see utils.power_of_ten) (ST)
* Better ROI color control (ST)
* Support load atlas from several extensions (LT)
* Support adding custom ROI (LT)

Sleep
^^^^^

* Better integration of non-supported files (compatibility with MNE)  (ST)
* Command-line control (LT)
* De-noising (LT)
* Zero re-referencing (LT)
* Automatic-scoring (LT)

Figure
^^^^^^

* Improve memory efficiency when loading files in a loop.
