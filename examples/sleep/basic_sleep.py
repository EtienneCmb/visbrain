"""
Basic configuration
===================

This example demonstrate how to open Sleep.

Two windows will then appear :

* The first one ask a proper dataset (required)
* The second one ask for an hypnogram (optional). If None, an empty one is used

.. image:: ../../picture/picsleep/ex_basic_sleep.png
"""
from visbrain import Sleep

Sleep().show()
