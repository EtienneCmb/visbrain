"""
Load an existing colorbar configuration file
============================================

The configuration is in a config.txt file and is loaded to reproduce the
colorbar configuration.

Configuration file 1 (config_1.txt) :
https://drive.google.com/open?id=0B6vtJiCQZUBvREFEX08zSWRFbzQ
Configuration file 2 (config_2.txt) :
https://drive.google.com/open?id=0B6vtJiCQZUBvWVM3U3RrSWxkeE0

.. image:: ../../picture/piccbar/ex_load_existing_config.png
"""
from visbrain import Colorbar

Colorbar(config='config_1.txt').show()
