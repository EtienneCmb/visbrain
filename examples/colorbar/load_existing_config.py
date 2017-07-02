"""
Load an existing colorbar configuration file
============================================

The configuration is in a config.txt file and is loaded to reproduce the
colorbar configuration.
"""
from visbrain import Colorbar

Colorbar(config='config.txt').show()
