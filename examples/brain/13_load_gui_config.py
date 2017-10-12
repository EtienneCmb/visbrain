"""
Load Graphical User Interface configuration
===========================================

Load a Graphical User Interface configuration file and retrieve previous
session.

Load this file :

* From the menu File/load/GUI config
* Using the load_config() method

Download configuration file (config.txt) :
https://www.dropbox.com/s/o0ljy16mpz7mmxu/brain_config.txt?dl=1

.. image:: ../../picture/picbrain/ex_load_config.png
"""
from visbrain import Brain
from visbrain.io import download_file, path_to_visbrain_data

# Define an empty Brain instance
vb = Brain()

# Load the configuration file :
download_file('brain_config.txt')
vb.load_config(path_to_visbrain_data('brain_config.txt'))

"""
Alternatively, if you want you can use the following method to save a new
configuration file or using the menu File/Save/GUI config
"""
# vb.save_config('new_config_file.txt')

vb.show()
