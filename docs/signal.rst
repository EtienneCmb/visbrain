.. _SignalModule:

:class:`Signal`
###############

.. figure::  picture/ico/signal_ico.png
   :align:   center

Description
-----------

:class:`Signal` is a data-mining module for 1-D, 2-D and 3-D datasets. It tries to offer a convenient way to inspect datasets, locate bad trials and reveal time-frequency properties. It is subdivided into to two distinct components :

* **The grid** : each datasets is re-arranged into a clickable 2-D grid so that all of the time-series of a dataset are represented inside. This idea of a grid was originally present into the `VisPy examples <https://github.com/vispy/vispy/blob/master/examples/demo/gloo/realtime_signals.py>`_ and has been adapted for brain signals.
* **The signal canvas** : the second layout display one trial at a time. This trial can either be represented as a continuous line or markers. It's also possible to compute the histogram, time-frequency map or PSD.

.. figure::  picture/picsignal/signal_presentation.png
   :align:   center

   (left) continuous line, markers, histogram, time-frequency map, power spectrum density (PSD), (right) grid representation

Main features
~~~~~~~~~~~~~

* **Grid disposition**
    * 2-D and 3-D datasets are disposed into a grid for an overview of an entire dataset
    * Zoom, translate and double click on a signal to enlarge it
* **Signal inspection**
    * Plot one time-series at a time
    * Navigate across all of the time-series present in the dataset
    * Change the plotting form (continuous line, markers, histogram, time-frequency map, power spectrum density (PSD))
    * Load and export annotated trials
* **Tools**
    * De-trending and de-meaning
    * Filtering (lowpass, highpass, bandpass, bandstop)
    * Extract the amplitude, phase or power in specific frequency bands
    * Take a screenshot (of the entire window, or the grid canvas only or of the signal canvas only)

Import and use Signal
~~~~~~~~~~~~~~~~~~~~~

The :class:`Signal` module can be imported as follow :

.. code-block:: python

    from visbrain import Signal


Examples and datasets
~~~~~~~~~~~~~~~~~~~~~

To try out this module, check out the `Signal example <http://visbrain.org/auto_examples/index.html#signal-examples>`_ scripts.


.. GUI description
.. ~~~~~~~~~~~~~~~

.. Components
.. ^^^^^^^^^^

API
------

Signal class
~~~~~~~~~~~~

.. currentmodule:: visbrain

.. autoclass:: Signal
    :members: show, set_xlim, set_ylim, set_signal_index, set_signal_form, screenshot

    .. rubric:: Methods

    .. autosummary::
        ~visbrain.Signal.show
        ~visbrain.Signal.set_xlim
        ~visbrain.Signal.set_ylim
        ~visbrain.Signal.set_signal_index
        ~visbrain.Signal.set_signal_form
        ~visbrain.Signal.screenshot


Shortcuts
---------

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