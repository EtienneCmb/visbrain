.. _TopoModule:

Topo
====

.. raw:: html

  <div class="jumbotron">
    <h1 class="display-3">Quick description <img alt="_images/topo_ico.png" src="_images/topo_ico.png" width="150" height="150" align="right"></h1>
    <p class="lead">Topo is a GUI based module for topographic representations.</p>
    <hr class="my-4">
    <p>

Checkout the API of the :class:`visbrain.Topo` class. If you need help with the :class:`Topo` module, ask your questions in the dedicated `gitter Topo chat <https://gitter.im/visbrain-python/Topo?utm_source=share-link&utm_medium=link&utm_campaign=share-link>`_

.. raw:: html

    <img alt="_images/ex_topoplot_plotting_properties.png" src="_images/ex_topoplot_plotting_properties.png" align="center"></p>
  </div>

.. contents:: Contents
   :local:
   :depth: 2

Main features
~~~~~~~~~~~~~

.. raw:: html

    <div class="grid-container">
        <div class="grid-item">
            <div class="alert alert-dismissible alert-primary">
              <b>Display topographic map</b>
              <ul>
                <li>Find coordinates according to channel names</li>
                <li>Add connectivity edges</li>
                <li>Support multiple coordinate systems</li>
                <li>Highly controllable colorbar</li>
              </ul>
            </div>
        </div>
        <div class="grid-item">
            <div class="alert alert-dismissible alert-primary">
              <b>Grid representation</b>
              <ul>
                <li>Display topoplot into a highly controllable grid.</li>
                <li>Add either one colorbar per topoplot or one shared colorbar across topoplot</li>
              </ul>
            </div>
        </div>
    </div>


Import and use Topo
~~~~~~~~~~~~~~~~~~~

The :class:`Topo` module can be imported as follow :

.. code-block:: python

    from visbrain import Topo

Examples
~~~~~~~~

.. include:: generated/visbrain.Topo.examples

.. raw:: html

    <div style='clear:both'></div>
