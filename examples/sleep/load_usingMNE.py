"""
Load a file using MNE-python
============================

This example shows how to load data using MNE-Python package.
https://martinos.org/mne/stable/index.html

Install MNE-python : pip install mne

A full list of supported format can be found here:
https://martinos.org/mne/stable/python_reference.html#reading-raw-data

Required dataset at :
https://drive.google.com/drive/folders/0B6vtJiCQZUBvRjc3cFFYcmFIeW8?usp=sharing

.. image:: ../../picture/picsleep/ex_LoadMNE.png
"""
from mne import io
from visbrain import Sleep

raw = io.read_raw_brainvision(vhdr_fname='sub-02.vhdr', preload=True)

# Extract data, sampling frequency and channels names
data, sf, chan = raw._data, raw.info['sfreq'], raw.info['ch_names']

# Now, pass all the arguments to the Sleep module :
Sleep(data=data, sf=sf, channels=chan, hypno_file='sub-02.hyp').show()
