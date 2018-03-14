.. -*- mode: rst -*-

.. image:: https://travis-ci.org/EtienneCmb/visbrain.svg?branch=master
    :target: https://travis-ci.org/EtienneCmb/visbrain

.. image:: https://ci.appveyor.com/api/projects/status/fdxhhmpagms1so8l/branch/master?svg=true
    :target: https://ci.appveyor.com/project/EtienneCmb/visbrain/branch/master

.. image:: https://circleci.com/gh/EtienneCmb/visbrain/tree/master.svg?style=svg
    :target: https://circleci.com/gh/EtienneCmb/visbrain/tree/master

.. image:: https://codecov.io/gh/EtienneCmb/visbrain/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/EtienneCmb/visbrain

.. image:: https://badge.fury.io/py/visbrain.svg
  :target: https://badge.fury.io/py/visbrain

Visbrain
########

.. figure::  https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/visbrain.png
   :align:   center


**Visbrain** is an open-source python 3 package dedicated to brain signals visualization. It is based on top of `VisPy <http://vispy.org/>`_ and PyQt and is distributed under the 3-Clause BSD license. We also provide an on line `documentation <http://visbrain.org>`_, `examples and datasets <http://visbrain.org/auto_examples/>`_ and can also be downloaded from `PyPi <https://pypi.python.org/pypi/visbrain/>`_.

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

* NumPy >= 1.13
* SciPy
* VisPy >= 0.5.0
* Matplotlib >= 1.5.5
* PyQt5
* Pillow

User installation
-----------------

Install Visbrain :

.. code-block:: shell

    pip install visbrain

We also strongly recommend to install *pandas* and *pyopengl* :

.. code-block:: shell

    pip install pandas PyOpenGL PyOpenGL_accelerate

Modules
=======

.. figure::  https://github.com/EtienneCmb/visbrain/blob/master/docs/picture/visbrain_readme.png
   :align:   center

* `Brain <http://visbrain.org/brain.html>`_ : visualize EEG/MEG/Intracranial data, connectivity in a standard MNI 3D brain (see `Brain examples <http://visbrain.org/auto_examples/index.html#brain-examples>`_).
* `Sleep <http://visbrain.org/sleep.html>`_ : visualize and analyze polysomnographic sleep data (see `Sleep examples <http://visbrain.org/auto_examples/index.html#sleep-examples>`_).
* `Signal <http://visbrain.org/signal.html>`_ : data-mining module for time-series inspection (see `Signal examples <http://visbrain.org/auto_examples/index.html#signal-examples>`_).
* `Topo <http://visbrain.org/topo.html>`_ : display topographical maps (see `Topo examples <http://visbrain.org/auto_examples/index.html#topoplot-examples>`_).
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
