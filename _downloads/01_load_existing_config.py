"""
Load an existing colorbar configuration file
============================================

The configuration is in a config.txt file and is loaded to reproduce the
colorbar configuration.

.. image:: ../../picture/piccbar/ex_load_existing_config.png
"""
from visbrain import Colorbar

Colorbar(config='config_1.txt').show()
