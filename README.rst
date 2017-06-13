.. -*- mode: rst -*-

.. image:: https://travis-ci.org/EtienneCmb/visbrain.svg?branch=master
    :target: https://travis-ci.org/EtienneCmb/visbrain

Visbrain
########

.. figure::  https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/visbrain.png
   :align:   center


**Visbrain** is an open-source python package and provides hardware accelerated visualizations mainly for neuroscientific data. It is based on top `VisPy <http://vispy.org/>`_ and PyQt and distributed under the 3-Clause BSD license. We also provide an online `documentation <http://vispy.org/>`_, `examples <https://github.com/EtienneCmb/visbrain/tree/master/examples>`_ with datasets.

Right now, four modules are implemented, with the first three coming with a modular graphical interface :

* :ref:`brainmod` : visualize EEG/MEG/Intracranial data and connectivity in a standard MNI 3D brain
* :ref:`sleepmod` : visualize polysomnographic data and hypnogram edition
* :ref:`ndvizmod` : visualize multidimensional data and basic plotting forms
* :ref:`figmod` : figure-layout for high-quality figures

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

.. _brainmod:

Brain
-----

The `Brain <http://etiennecmb.github.io/visbrain/brain.html>`_ module is primarily designed for visualizations within a 3D opaque/transparent brain and can be used for :

* Integrate EEG/MEG/Intracranial sources/electrodes and connectivity
* Display Regions of Interest (ROI) based on Brodmann or AAL atlases.
* Project source's activity onto the brain/ROI surface
* Export in HD pictures with auto-cropping functionalities
* GUI or command line control

.. figure::  https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/example.png
   :align:   center

   `Examples and datasets <https://github.com/EtienneCmb/visbrain/tree/master/examples>`_


.. _sleepmod:

Sleep
-----

`Sleep <http://etiennecmb.github.io/visbrain/sleep.html>`_ 

Sleep's main functionalities are :

* Load BrainVision, Micromed or European Data Format. All other files can be loaded using `MNE Python <http://mne-tools.github.io/stable/python_reference.html?highlight=io#module-mne.io>`_ and pass as raw data
* Visualize polysomnographic data / spectrogram / topographic maps
* Load, edit and save hypnogram
* Performs automatic event detections (Spindles / REM / Peaks / Slow waves / K-complex / Muscle twiches)
* Signal processing tools (filtering / wavelets / power...) and re-referencing (either to a single channel or common average or bipolarization)


.. figure::  https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/example.png
   :align:   center

   `Examples and datasets <https://drive.google.com/drive/folders/0B6vtJiCQZUBvRjc3cFFYcmFIeW8?usp=sharing>`_

.. _ndvizmod:

Ndviz
-----

The [Ndviz](http://etiennecmb.github.io/visbrain/ndviz.html) module help you to visualize multi-dimentional data in a memory efficient way.

- Nd-plot: visualize all of your signals in one grid
- 1d-plot: visualize each signal individually in one of the several forms below
	- As a nice continuous line
	- As a cloud of points
	- As a histogram
	- As an image
	- In the time-frequency domain using the spectrogram

	Each object inherit from a large number of color control or different settings.

![ndviz](https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/ndviz_example.png "Ndviz : data mining")


.. _figuremod:

Figure
------



Contributors
============

Main contributors
-----------------

* [Etienne Combrisson](http://etiennecmb.github.io)
* [Raphael Vallat](https://raphaelvallat.github.io/)
* [Dmitri Altukchov](https://github.com/dmalt)
* [David Meunier](https://github.com/davidmeunier79)
* [Tarek Lajnef](https://github.com/TarekLaj)
* [Karim Jerbi](www.karimjerbi.com)

Thx to...
---------

*Christian O'Reilly, Perrine Ruby, JB Einchenlaub, kevroy314, Annalisa Pascarella, Thomas Thiery, Yann Harel, Anne-Lise Saive, Golnush Alamian...*
