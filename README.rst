.. -*- mode: rst -*-

.. image:: https://travis-ci.org/EtienneCmb/visbrain.svg?branch=master
    :target: https://travis-ci.org/EtienneCmb/visbrain

.. image:: https://codecov.io/gh/EtienneCmb/visbrain/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/EtienneCmb/visbrain

.. image:: https://badge.fury.io/py/visbrain.svg
  :target: https://badge.fury.io/py/visbrain
    
Visbrain
########

.. figure::  https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/visbrain.png
   :align:   center


**Visbrain** is an open-source python 3 package and provides hardware accelerated visualizations mainly for neuroscientific data. It is based on top of `VisPy <http://vispy.org/>`_ and PyQt and is distributed under the 3-Clause BSD license. We also provide an on line `documentation <http://visbrain.org>`_, `examples and datasets <http://visbrain.org/auto_examples/>`_ and can also be downloaded from `PyPi <https://pypi.python.org/pypi/visbrain/>`_.

Important links
===============

* Official source code repository : https://github.com/EtienneCmb/visbrain
* Online documentation : http://visbrain.org
* Visbrain `chat room <https://gitter.im/visbrain-python/chatroom?utm_source=share-link&utm_medium=link&utm_campaign=share-link>`_


Installation
============

Dependencies
------------

Visbrain requires :

* NumPy
* SciPy
* VisPy (*development version*)
* Matplotlib >= 1.5.5
* PyQt5
* Pillow

User installation
-----------------

Install the latest VisPy version from Github :

.. code-block:: shell

    pip install -e git+https://github.com/vispy/vispy#egg=vispy-dev

Then, install Visbrain :

.. code-block:: shell

    pip install visbain

We also strongly recommend to install *pyopengl* :

.. code-block:: shell

    pip install PyOpenGL PyOpenGL_accelerate

Modules
=======

.. figure::  https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/visbrain_readme.png
   :align:   center

* `Brain <http://visbrain.org/brain.html>`_ : visualize EEG/MEG/Intracranial data, connectivity in a standard MNI 3D brain (see `Brain examples <http://visbrain.org/auto_examples/index.html#brain-examples>`_).
* `Sleep <http://visbrain.org/sleep.html>`_ : visualize polysomnographic data and hypnogram edition (see `Sleep examples <http://visbrain.org/auto_examples/index.html#sleep-examples>`_).
* `Topo <http://visbrain.org/topo.html>`_ : display topographical maps (see `Topo examples <http://visbrain.org/auto_examples/index.html#topoplot-examples>`_).
* `Ndviz <http://visbrain.org/ndviz.html>`_ : visualize multidimensional data and basic plotting forms (see `Ndviz examples <http://visbrain.org/auto_examples/index.html#ndviz-examples>`_).
* `Figure <http://visbrain.org/figure.html>`_ : figure-layout for high-quality publication-like figures (see `Figure examples <http://visbrain.org/auto_examples/index.html#figure-examples>`_).
* `Colorbar <http://visbrain.org/colorbar.html>`_ : colorbar editor (see `Colorbar examples <http://visbrain.org/auto_examples/index.html#colorbar-examples>`_).


Contribution
============

Main developers
---------------

* `Etienne Combrisson <http://etiennecmb.github.io>`_
* `Raphael Vallat <https://raphaelvallat.github.io>`_

With the help of
----------------

*Karim Jerbi, Christian O'Reilly, David Meunier, Dmitri Altukchov, Tarek Lajnef, Perrine Ruby, JB Einchenlaub, kevroy314, Annalisa Pascarella, Thomas Thiery, Yann Harel, Anne-Lise Saive, Golnush Alamian*
