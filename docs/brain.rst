.. _BrainModule:

Brain
=====

.. raw:: html

  <div class="jumbotron">
    <h1 class="display-3">Quick description <img alt="_static/ico/brain_ico.png" src="_static/ico/brain_ico.png" width="150" height="150" align="right"></h1>
    <p class="lead">Brain is a flexible graphical user interface for 3D visualizations on an MNI brain. It can be use to display deep sources, connectivity, region of interest etc.</p>
    <hr class="my-4">
    <p>

Checkout the API of the :class:`visbrain.gui.Brain` class. If you need help with the *Brain* module, ask your questions in the dedicated `gitter Brain chat <https://gitter.im/visbrain-python/Brain?utm_source=share-link&utm_medium=link&utm_campaign=share-link>`_

.. raw:: html

    <img alt="_static/brain/brain_description.png" src="_static/brain/brain_description.png" align="center"></p>
  </div>

.. contents:: Contents
   :local:
   :depth: 2

.. ##########################################################################
..                                 DESCRIPTION
.. ##########################################################################

Main features
~~~~~~~~~~~~~

.. raw:: html

    <div class="grid-container">
        <div class="grid-item">
            <div class="alert alert-dismissible alert-primary">
              <b>Graphical User Interface</b>
              <ul>
                <li>Modular and responsive GUI</li>
                <li>Take screenshot with controllable dpi</li>
                <li>Save the GUI state (buttons, sliders, checkbox...)</li>
              </ul>
            </div>
        </div>
        <div class="grid-item">
            <div class="alert alert-dismissible alert-primary">
              <b>Main brain templates</b>
              <ul>
                <li>Zoom, translate and rotate the brain</li>
                <li>Control the brain appearance, transparency, hemisphere...</li>
                <li>Import custom templates</li>
              </ul>
            </div>
        </div>
        <div class="grid-item">
            <div class="alert alert-dismissible alert-primary">
              <b>Sources</b>
              <ul>
                <li>Add sources to the scene (EEG, MEG, intra-cranial...)</li>
                <li>Connect those sources (Connectivity with several color properties)</li>
                <li>Project source's activity onto the surface</li>
                <li>Localize source's location using either the Brodmann atlas, the Automated Anatomical Labeling (AAL) or any custom atlas.</li>
              </ul>
            </div>
        </div>
        <div class="grid-item">
            <div class="alert alert-dismissible alert-primary">
              <b>Region Of Interest</b>
              <ul>
                <li>Display ROI inside translucent MNI brain</li>
                <li>Define and use custom ROI</li>
                <li>Project source's activity onto ROI</li>
              </ul>
            </div>
        </div>
        <div class="grid-item">
            <div class="alert alert-dismissible alert-primary">
              <b>Cross-sections</b>
              <ul>
                <li>Display brain sections</li>
                <li>Localize sources in the cross section</li>
                <li>Use a nifti file</li>
              </ul>
            </div>
        </div>
        <div class="grid-item">
            <div class="alert alert-dismissible alert-primary">
              <b>Others</b>
              <ul>
                <li>Display volumes</li>
                <li>Display time-series, pictures etc.</li>
                <li>Display vectors</li>
              </ul>
            </div>
        </div>
    </div>

Import and use Brain
~~~~~~~~~~~~~~~~~~~~

The *Brain* module can be imported as follow :

.. code-block:: python

    from visbrain.gui import Brain

GUI description
~~~~~~~~~~~~~~~

Components
^^^^^^^^^^

The *Brain* graphical user interface is subdivided into three main parts :

* **Menu** (*Save/load GUI config, take a screenshot*...)
* **Settings panel** (*display by default*)
* **Main canvas** where the brain is displayed
* **Colorbar canvas** (*hide by default*)
* **Cross-sections canvas** (*hide by default*)


Settings panel tabs
^^^^^^^^^^^^^^^^^^^

* Settings tab (*background color, object opacity and slice, light*)
* Brain tab (*brain template, ROI, cross-sections, volume*)
* Sources tab (*source's properties, text, cortical projection and repartition, time-series, pictures*)
* Connect tab (*connectivity settings*)
* Cbar tab (*colorbar properties of the selected object*)

.. _brainshortcuts:

Shortcuts
^^^^^^^^^

==============          ==============================================
Keys                    Description
==============          ==============================================
<space>                 Brain transparency
<delete>                Reset camera
0                       Top view
1                       Bottom view
2                       Left view
3                       Right view
4                       Front view
5                       Back view
b                       Display / hide the brain
x                       Display / hide cross-sections
v                       Display / hide volume
s                       Display / hide sources
t                       Display / hide connectivity
r                       Display / hide Region Of Interest (ROI)
c                       Display / hide colorbar
a                       Auto-scale colormap
"+"                     Increase brain opacity
"-"                     Decrease brain opacity
CTRL + p                Run the cortical projection
CTRL + r                Run the cortical repartition
CTRL + d                Display / hide quick settings panel
CTRL + n                Screenshot window
CTRL + w                Screenshot of the entire window
CTRL + t                Show the shortcuts panel
CTRL + q                Exit
==============          ==============================================

.. ##########################################################################
..                                 TUTORIAL
.. ##########################################################################

MNI templates
~~~~~~~~~~~~~

.. figure::  _static/brain/brain_templates.png
   :align:   center

By default, *Brain* comes with three brain templates respectively B1 (with cerebellum), B2 and B3 (smoothest).

Further brain templates can be downloaded `here <https://drive.google.com/open?id=0B6vtJiCQZUBvd0xfTHJqcHg2bTA>`_.


Sources
~~~~~~~

.. figure::  _static/brain/brain_sources.png
   :align:   center

Sources can be added to the scene using (x, y, z) MNI coordinates and comes with a relatively large number of properties (radius, color, shape...). Source's array of coordinates must be have a shape of (N, 3) with **N** the number of sources. In addition, several objects can be attached to sources :

* **Text :** add a text to each source.
* **Source's data :** must be (N,) vector of data (for instance beta power, entropy, amplitude...). The radius of each source is then proportional to the data attached to it. This activity can be projected onto the brain surface using the cortical projection.
* **Connectivity :** must be a (N, N) upper triangular array describing how to connect sources
* **Time-series and/or pictures** : finally, it's also possible to visualize signals (such as time-series, spectral signals...) and 2-D pictures (time-frequency maps, comodulogram...)


Cortical projection and repartition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure::  _static/brain/brain_projection.png
   :align:   center

   Cortical projection of source's activity (Left) and source's repartition (Right).

* **Cortical projection :** correspond to the projection of source's activity onto the brain (or ROI) surface.
* **Cortical repartition :** correspond to the number of sources contributing to each vertex of the surface. This is particularly convenient to inspect how sources are distributed on the surface.

Both methods use a **radius** parameter and only vertices with an euclidian distance under **radius** are going to be considered. From the GUI, those functions can be executed from the menu *Project*, from the tab *Sources/Properties/Projection*, using keyboard :ref:`brainshortcuts` or *Brain* methods.


Connect sources
^^^^^^^^^^^^^^^

.. figure::  _static/brain/brain_connect.png
   :align:   center

   Example of connectivity.

Sources can be connected together using connectivity links. *Brain* provides three ways of coloring those links :

* **Strength :** color each link according to the connectivity strength
* **Count :** color each connectivity node according to the number of connections to it
* **Density :** color each link according to the number of existing links in a controllable sphere.


Attach time-series and/or pictures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure::  _static/brain/brain_tspic.png
   :align:   center

   Attach time-series (Left) and pictures (Right) to sources.

As a complement, *Brain* provides the ability to visualize directly into the MNI brain time-series and pictures.


.. warning::

   In the current 0.3.0 visbrain version, time-series and pictures don't rotate with the brain. As a consequence those elements can only be visualized in axial view. This should be solved in next release.

Volume
~~~~~~

Brain templates are surfaces defined by vertices and faces. In contrast, volumes are defined with a 3-D array (Nx, Ny, Nz). There is three scenarios where volumes can be used in *Brain*:

* **Cross-sections :** inspect volumes using slices
* **Region Of Interest (ROI) :** display deep brain regions
* **3-D volume rendering :** use VisPy.visuals.Volume rendering methods (mip, translucent, additive and iso)

Those volumes can be used to visualize nifti, dycom or any image files. By default, *Brain* comes with two volume files : **Brodmann areas** and **Anatomical Automatic Labeling (AAL)**.

Cross-sections
^^^^^^^^^^^^^^

.. figure::  _static/brain/brain_crossec.png
   :align:   center

   Cross-sections of a Nifti volume

Cross-sections correspond to an axial, sagittal and coronal slice of the volume and can either be visualize in 3-D (inside the brain template) or in slitted view


Region Of Interest (ROI)
^^^^^^^^^^^^^^^^^^^^^^^^

.. figure::  _static/brain/brain_roi.png
   :align:   center

   Cortical projection on the thalamus (Left) and cortical repartition on Brodmann area 4 and 6.

If a volume is provided with corresponding labels, ROIs can be extracted and then be transformed into a mesh, compatible with source's projection methods.


Colorbar control
~~~~~~~~~~~~~~~~

.. figure::  _static/brain/brain_cbar.png
   :align:   center

   Colorbar example.

The colorbar can be controlled for individual objects including :

* **Connectivity** (*if defined*)
* **Pictures** (*if defined*)
* **Projections** (*if defined*)

Examples
~~~~~~~~

.. include:: generated/visbrain.gui.Brain.examples

.. raw:: html

    <div style='clear:both'></div>