.. _ChangelogFutur:

Changelog and future directions
###############################

Changelog
---------

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

* conda installation
* Independent of the VisPy developer version for better installation (ST)
* Code style improvements (flake8 and numpydoc) (ST)
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
