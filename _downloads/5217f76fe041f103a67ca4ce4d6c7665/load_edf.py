"""
Load EDF file
=============

This example demonstrate how to load an EDF file.

Required dataset at :
https://www.dropbox.com/s/bj1ra95rbksukro/sleep_edf.zip?dl=1

.. image:: ../../_static/examples/ex_LoadEDF.png
"""
import os
from visbrain.gui import Sleep
from visbrain.io import download_file, path_to_visbrain_data

###############################################################################
#                               LOAD YOUR FILE
###############################################################################
download_file('sleep_edf.zip', unzip=True, astype='example_data')
target_path = path_to_visbrain_data(folder='example_data')

dfile = os.path.join(target_path, 'excerpt2.edf')
hfile = os.path.join(target_path, 'Hypnogram_excerpt2.txt')
cfile = os.path.join(target_path, 'excerpt2_config.txt')

# Open the GUI :
Sleep(data=dfile, hypno=hfile, config_file=cfile).show()
