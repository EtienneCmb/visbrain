.. -*- mode: rst -*-

.. image:: https://travis-ci.org/EtienneCmb/visbrain.svg?branch=master
    :target: https://travis-ci.org/EtienneCmb/visbrain

Visbrain
########

.. figure::  https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/visbrain.png
   :align:   center


**Visbrain** is an open-source python package and provides hardware accelerated visualizations mainly for neuroscientific data. It is based on top of `VisPy <http://vispy.org/>`_ and PyQt and is distributed under the 3-Clause BSD license. We also provide an online `documentation <http://etiennecmb.github.io/visbrain/>`_, `examples and datasets <https://github.com/EtienneCmb/visbrain/tree/master/examples>`_ and can also be downloaded from `PyPi <https://pypi.python.org/pypi/visbrain/>`_.

Right now, four modules are implemented, with the first three coming with a modular graphical interface :

* **Brain** : visualize EEG/MEG/Intracranial data and connectivity in a standard MNI 3D brain.
* **Sleep** : visualize polysomnographic data and hypnogram edition.
* **Ndviz** : visualize multidimensional data and basic plotting forms.
* **Figure** : figure-layout for high-quality publication-like figures.

Installation
============

Dependencies
------------

Visbrain requires :

* Numpy
* Scipy
* Vispy (*development version*)
* Matplotlib <= 1.5.1
* PyQt4
* Pillow

User installation
-----------------

In a terminal, create and activate a 3.5 Python environment with the correct PyQt4 version :

.. code-block:: shell

    conda create --yes  -n visbrain python=3.5 numpy scipy pillow matplotlib=1.5.1 pip
    activate visbrain

Install the latest VisPy version from Github :

.. code-block:: shell

    pip install -e git+https://github.com/vispy/vispy#egg=vispy-dev

Finally, install Visbrain :

.. code-block:: shell

    pip install visbain

Modules
=======

Brain
-----

The `Brain <http://etiennecmb.github.io/visbrain/brain.html>`_ module is primarily designed for visualizations within a 3D opaque/transparent brain and can be used for :

* Integrate EEG/MEG/Intracranial sources/electrodes and connectivity.
* Display Regions of Interest (ROI) based either on Brodmann or AAL atlases.
* Project source's activity onto the brain/ROI surface.
* An extended control of colours. 
* Export in HD pictures with auto-cropping functionalities.
* GUI or command line control.
* `Examples and datasets <https://github.com/EtienneCmb/visbrain/tree/master/examples>`_.

.. figure::  https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/example.png
   :align:   center

Sleep
-----

`Sleep <http://etiennecmb.github.io/visbrain/sleep.html>`_ is a GUI based module for sleep data visualization and edition under Python. Main functionalities are :

* Load BrainVision, Micromed or European Data Format. Other file formats can be loaded using `MNE Python <http://mne-tools.github.io/stable/python_reference.html?highlight=io#module-mne.io>`_ and then pass as raw data.
* Visualize polysomnographic data / spectrogram / topographic maps.
* Load, edit and save hypnogram data or as publication-ready figures.
* Perform automatic event detections (Spindles / REM / Peaks / Slow waves / K-complex / Muscle twitches).
* Signal processing tools (filtering / wavelets / power...) and re-referencing (either to a single channel, common average or bipolarization).
* `Examples and datasets <https://drive.google.com/drive/folders/0B6vtJiCQZUBvRjc3cFFYcmFIeW8?usp=sharing>`_.

.. figure::  https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/Sleep_main.png
   :align:   center

Ndviz
-----

`Ndviz <http://etiennecmb.github.io/visbrain/ndviz.html>`_ was designed to visualize multidimensional data and also includes basic plots :

* Visualize large datasets into a grid.
* Basic plotting forms (continuous line / cloud of points / image).
* Compute histogram / spectrogram.
* Swap data dimensions from the GUI.
* `Examples <https://github.com/EtienneCmb/visbrain/tree/master/examples/ndviz>`_.

.. figure::  https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/ndviz_example.png
   :align:   center

Figure
------

`Figure <http://etiennecmb.github.io/visbrain/figure.html>`_ is the only module which do not rely on a GUI or VisPy. It's a Matplotlib wrapper to simplify scientific figures production and allows :

* Load images and grid disposition.
* Add x/y labels and titles.
* Simple colorbar control.
* Export the final figure with dpi control.
* `Examples <https://github.com/EtienneCmb/visbrain/tree/master/examples/figure>`_.


Contributors
============

Main contributors
-----------------

* `Etienne Combrisson <http://etiennecmb.github.io>`_
* `Raphael Vallat <https://raphaelvallat.github.io>`_
* `Dmitri Altukchov <https://github.com/dmalt>`_
* `David Meunier <https://github.com/davidmeunier79>`_
* `Tarek Lajnef <https://github.com/TarekLaj>`_
* `Karim Jerbi <www.karimjerbi.com>`_

Thx to...
---------

Christian O'Reilly, Perrine Ruby, JB Einchenlaub, kevroy314, Annalisa Pascarella, Thomas Thiery, Yann Harel, Anne-Lise Saive, Golnush Alamian
