"""
Load a file using MNE-python
============================

This example shows how to load data using MNE-Python package.
https://martinos.org/mne/stable/index.html

Install MNE-python : pip install mne

A full list of supported format can be found here:
https://martinos.org/mne/stable/python_reference.html#reading-raw-data

Required dataset at :
https://www.dropbox.com/s/t2bo9ufvc3f8mbj/sleep_brainvision.zip?dl=1

.. image:: ../../_static/examples/ex_LoadMNE.png
"""
import os
from mne import io
from visbrain.gui import Sleep
from visbrain.io import download_file, path_to_visbrain_data

###############################################################################
#                               LOAD YOUR FILE
###############################################################################
# Download dataset :
download_file("sleep_brainvision.zip", unzip=True, astype='example_data')
target_path = path_to_visbrain_data(folder='example_data')

dfile = os.path.join(target_path, 'sub-02.vhdr')
hfile = os.path.join(target_path, 'sub-02.hyp')

# Read raw data using MNE-python :
raw = io.read_raw_brainvision(vhdr_fname=dfile, preload=True)

# Extract data, sampling frequency and channels names
data, sf, chan = raw._data, raw.info['sfreq'], raw.info['ch_names']

# Now, pass all the arguments to the Sleep module :
Sleep(data=data, sf=sf, channels=chan, hypno=hfile).show()

# Alternatively, these steps can be done automatically by using the 'use_mne'
# input argument of sleep
# Sleep(data=dfile, hypno=hfile, use_mne=True).show()
