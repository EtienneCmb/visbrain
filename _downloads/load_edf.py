"""
Load EDF file
=============

This example demonstrate how to load an EDF file.

Required dataset at :
https://www.dropbox.com/s/hc18bgn2hlnmiph/sleep_edf.zip?dl=1

.. image:: ../../picture/picsleep/ex_LoadEDF.png
"""
from visbrain import Sleep
from visbrain.io import download_file

download_file('sleep_edf.zip', unzip=True)

Sleep(data='excerpt2.edf', hypno='Hypnogram_excerpt2.txt').show()
