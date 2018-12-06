"""
Load a Matlab file
==================

This example demonstrate how to load an ELAN file.

Required dataset at :
https://www.dropbox.com/s/bmfc2u55xsejbaf/sleep_matlab.zip?dl=1

.. image:: ../../_static/examples/ex_LoadMatlab.png
"""
import os
import numpy as np
from scipy.io import loadmat

from visbrain.gui import Sleep
from visbrain.io import download_file, path_to_visbrain_data

###############################################################################
#                               LOAD YOUR FILE
###############################################################################
# Download matlab file :
download_file("sleep_matlab.zip", unzip=True, astype='example_data')
target_path = path_to_visbrain_data(folder='example_data')

# Load the matlab file :
mat = loadmat(os.path.join(target_path, 's2_sleep.mat'))

# Get the data, sampling frequency and channel names :
raw_data = mat['data']
raw_sf = float(mat['sf'])
raw_channels = np.concatenate(mat['channels'].flatten()).tolist()
raw_hypno = mat['hypno'].flatten()

# Open the GUI :
Sleep(data=raw_data, sf=raw_sf, channels=raw_channels, hypno=raw_hypno).show()
