.. _TopoModule:

:py:class:`Topo`
================

.. figure::  picture/ico/topo_ico.png
   :align:   center

Description
-----------

:class:`Topo` is a GUI based module for topographic representations.

.. figure::  picture/pictopo/ex_topoplot_plotting_properties.png
   :align:   center

Help
~~~~

If you need help with the :class:`Topo` module, ask your questions in the dedicated `gitter Topo chat <https://gitter.im/visbrain-python/Topo?utm_source=share-link&utm_medium=link&utm_campaign=share-link>`_

Main features
~~~~~~~~~~~~~

* **Display topographic map**
    * Find coordinates according to channel names
    * Add connectivity edges
    * Support multiple coordinate systems
    * Highly controllable colorbar
* **Grid representation**
    * Display topoplot into a highly controllable grid.
    * Add either one colorbar per topoplot or one shared colorbar across topoplot

Import and use Topo
~~~~~~~~~~~~~~~~~~~

The :class:`Topo` module can be imported as follow :

.. code-block:: python

    from visbrain import Topo

Examples and datasets
~~~~~~~~~~~~~~~~~~~~~

Visit this page for a set of `examples <http://visbrain.org/auto_examples/index.html#topoplot-examples>`_.

API
---

Topo class
~~~~~~~~~~

.. currentmodule:: visbrain

.. autoclass:: Topo
    :members: show, add_topoplot, add_shared_colorbar

    .. rubric:: Methods

    .. autosummary::
        ~Topo.show
        ~Topo.add_topoplot
        ~Topo.add_shared_colorbar