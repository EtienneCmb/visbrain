"""
Load a Matlab file
==================

This example demonstrate how to load an ELAN file.

Required dataset at :
https://www.dropbox.com/s/6teybg0i1wgn9sk/sleep_matlab.zip?dl=1

.. image:: ../../picture/picsleep/ex_LoadMatlab.png
"""
import numpy as np
from scipy.io import loadmat

from visbrain import Sleep
from visbrain.io import download_file

# Download matlab file :
download_file('sleep_matlab.zip', unzip=True)

# Load the matlab file :
mat = loadmat('s2_sleep.mat')

# Get the data, sampling frequency and channel names :
raw_data = mat['data']
raw_sf = float(mat['sf'])
raw_channels = np.concatenate(mat['channels'].flatten()).tolist()
raw_hypno = mat['hypno'].flatten()

Sleep(data=raw_data, sf=raw_sf, channels=raw_channels, hypno=raw_hypno).show()
