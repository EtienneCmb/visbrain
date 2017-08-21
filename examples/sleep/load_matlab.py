"""
Load a Matlab file
==================

This example demonstrate how to load an ELAN file.

Required dataset at :
https://drive.google.com/drive/folders/0B6vtJiCQZUBvRjc3cFFYcmFIeW8?usp=sharing

.. image:: ../../picture/picsleep/ex_LoadMatlab.png
"""
from visbrain import Sleep
import numpy as np
from scipy.io import loadmat

mat = loadmat('s2_sleep.mat')

# Get the data, sampling frequency and channel names :
raw_data = mat['data']
raw_sf = float(mat['sf'])
raw_channels = np.concatenate(mat['channels'].flatten()).tolist()
raw_hypno = mat['hypno'].flatten()

Sleep(data=raw_data, sf=raw_sf, channels=raw_channels, hypno=raw_hypno,
      config_file='s2_config.txt').show()
