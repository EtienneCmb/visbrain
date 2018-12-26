.. _Introduction:

Presentation
============

Quick description
-----------------

Visbrain is an open-source `Python 3 <https://www.python.org/>`_ package, distributed under the 3-Clause BSD license and is dedicated to brain signals visualization. It is under heavy development and many functionalities are frequently added to the package, such as bug fixing, documentation improvements etc.

Visbrain use VisPy to render graphics. Taken from their website :

.. raw:: html

    <blockquote class="blockquote">
      <p class="mb-0">VisPy is a high-performance interactive 2D/3D data visualization library leveraging the computational power of modern Graphics Processing Units (GPUs) through the OpenGL library to display very large datasets.</p>
      <footer class="blockquote-footer">VisPy website : <a href="http://vispy.org">http://vispy.org</a></footer>
    </blockquote>



Structure
---------

Visbrain is mainly divided into two branches :

* **Modules** : modules comes with a graphical user interface (GUI) for interactions between plotted elements and parameters.
* **Objects** : objects are elementary bricks i.e. one visualization purpose per object. It's mainly designed for advanced users since objects are much more modular. See the :ref:`Objects` documentation and the API :class:`visbrain.objects`

======================  =======================================================
Module name             Description
======================  =======================================================
:ref:`BrainModule`      Visualizations involving a MNI brain
:ref:`SleepModule`      Visualize and score polysomnographic data
:ref:`SignalModule`     Visualize multi-dimensional datasets
:ref:`FigureModule`     Figure layout
======================  =======================================================

The visbrain structure is summarized below.

.. figure::  _static/visbrain_structure.png
   :align:   center

   Structure and hierarchy used in visbrain

Installation options
====================

Dependencies
------------

* NumPy and SciPy (>= 1.13)
* Matplotlib (>= 1.5.5)
* VisPy (>= 0.5.3)
* PyQt5
* PyOpenGL
* Pillow

Optional dependencies
---------------------

* Pandas & xlrd : table import / export
* Pillow : export figures
* Nibabel : read nifti files
* MNE-python : alternative to read sleep data files
* Tensorpac : compute and display phase-amplitude coupling
* lspopt : multitaper spectrogram
* imageio : for animated GIF export

Regular installation
--------------------

In order to install Visbrain, or to update it, run the following command in a terminal :

.. code-block:: shell

    pip install -U visbrain

Develop mode
------------

If you want to install visbrain in develop mode :

.. code-block:: shell

    git clone https://github.com/EtienneCmb/visbrain.git visbrain/
    cd visbrain/
    python setup.py develop 

From here you can switch to the latest features using :

.. code-block:: shell

    git checkout develop

If you don't want to clone the full package, run :

.. code-block:: shell

    pip install git+https://github.com/EtienneCmb/visbrain.git


Update visbrain
---------------
You can update visbrain using :

.. code-block:: shell

    pip install --upgrade visbrain