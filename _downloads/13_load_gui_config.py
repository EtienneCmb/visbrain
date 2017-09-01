"""
Load Graphical User Interface configuration
===========================================

Load a Graphical User Interface configuration file and retrieve previous
session.

Load this file :

* From the menu File/load/GUI config
* Using the load_config() method

Download configuration file (config.txt) :
https://drive.google.com/open?id=0B6vtJiCQZUBvUm9menhtUzVhS2M

.. image:: ../../picture/picbrain/ex_load_config.png
"""
from visbrain import Brain

# Define an empty Brain instance
vb = Brain()

# Load the configuration file :
vb.load_config('config.txt')

"""
Alternatively, if you want you can use the following method to save a new
configuration file or using the menu File/Save/GUI config
"""
# vb.save_config('new_config_file.txt')

vb.show()
