"""
Load ELAN files
===============

This example demonstrate how to load an ELAN file.

Required dataset at :
https://www.dropbox.com/s/95xvdqivpgk90hg/sleep_elan.zip?dl=1

.. image:: ../../_static/examples/ex_LoadElan.png
"""
import os
from visbrain.gui import Sleep
from visbrain.io import download_file, path_to_visbrain_data

###############################################################################
#                               LOAD YOUR FILE
###############################################################################
# Download dataset :
download_file("sleep_elan.zip", unzip=True, astype='example_data')
target_path = path_to_visbrain_data(folder='example_data')

dfile = os.path.join(target_path, 'sub-02.eeg')
hfile = os.path.join(target_path, 'sub-02.hyp')

# Open the GUI :
Sleep(data=dfile, hypno=hfile).show()
