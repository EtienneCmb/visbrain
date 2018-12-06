.. _SignalModule:

Signal
######

.. raw:: html

  <div class="jumbotron">
    <h1 class="display-3">Quick description <img alt="_static/ico/signal_ico.png" src="_static/ico/signal_ico.png" width="150" height="150" align="right"></h1>
    <p class="lead">Signal is a data-mining module for 1-D, 2-D and 3-D datasets. It tries to offer a convenient way to inspect datasets, locate bad trials and reveal time-frequency properties.</p>
    <hr class="my-4">
    <p>

Checkout the API of the :class:`visbrain.gui.Signal` class.

.. raw:: html

    <img alt="_static/signal/signal_presentation.png" src="_static/signal/signal_presentation.png" align="center"></p>
  </div>

.. contents:: Contents
   :local:
   :depth: 2

GUI Description
~~~~~~~~~~~~~~~

The GUI of the Signal module is subdivided into to two distinct components :

* **The grid** : each datasets is re-arranged into a clickable 2-D grid so that all of the time-series of a dataset are represented inside. This idea of a grid was originally present into the `VisPy examples <https://github.com/vispy/vispy/blob/master/examples/demo/gloo/realtime_signals.py>`_ and has been adapted for brain signals.
* **The signal canvas** : the second layout display one trial at a time. This trial can either be represented as a continuous line or markers. It's also possible to compute the histogram, time-frequency map or PSD.

Main features
~~~~~~~~~~~~~

.. raw:: html

    <div class="grid-container">
        <div class="grid-item">
            <div class="alert alert-dismissible alert-primary">
              <b>Grid disposition</b>
              <ul>
                <li>2-D and 3-D datasets are disposed into a grid for an overview of an entire dataset</li>
                <li>Zoom, translate and double click on a signal to enlarge it</li>
              </ul>
            </div>
        </div>
        <div class="grid-item">
            <div class="alert alert-dismissible alert-primary">
              <b>Signal inspection</b>
              <ul>
                <li>Plot one time-series at a time</li>
                <li>Navigate across all of the time-series present in the dataset</li>
                <li>Change the plotting form (continuous line, markers, histogram, time-frequency map, power spectrum density (PSD))</li>
                <li>Load and export annotated trials</li>
              </ul>
            </div>
        </div>
        <div class="grid-item">
            <div class="alert alert-dismissible alert-primary">
              <b>Tools</b>
              <ul>
                <li>De-trending and de-meaning</li>
                <li>Filtering (lowpass, highpass, bandpass, bandstop)</li>
                <li>Extract the amplitude, phase or power in specific frequency bands</li>
                <li>Take a screenshot (of the entire window, or the grid canvas only or of the signal canvas only)</li>
              </ul>
            </div>
        </div>
    </div>


Import and use Signal
~~~~~~~~~~~~~~~~~~~~~

The :class:`Signal` module can be imported as follow :

.. code-block:: python

    from visbrain.gui import Signal


Shortcuts
~~~~~~~~~

* go = Grid canvas only
* so = Signal canvas only

======================  =======================================================
Keys                    Description
======================  =======================================================
Double click (go)       Enlarge signal under the mouse cursor
n (so)                  Go to the next signal
b (so)                  Go to the previous signal
Double click (so)       Insert annotation
g                       Display / hide grid
s                       Display / hide signal
<delete> (go and so)    Reset the camera
CTRL + t                Display shortcuts
CTRL + d                Display / hide setting panel
CTRL + n                Take a screenshot
CTRL + q                Close Sleep graphical interface
======================  =======================================================

Examples
~~~~~~~~

.. include:: generated/visbrain.gui.Signal.examples

.. raw:: html

    <div style='clear:both'></div>