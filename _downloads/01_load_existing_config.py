"""
Load an existing colorbar configuration file
============================================

The configuration is in a config.txt file and is loaded to reproduce the
colorbar configuration.

Configuration files :
https://www.dropbox.com/s/5o1ph08rmpft200/cbar_config.zip?dl=0

.. image:: ../../picture/piccbar/ex_load_existing_config.png
"""
from visbrain import Colorbar
from visbrain.io import download_file, path_to_visbrain_data

download_file('cbar_config.zip', unzip=True, remove_archive=True)
Colorbar(config=path_to_visbrain_data('config_1.txt')).show()
