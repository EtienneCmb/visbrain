"""
Load EDF file
=============

This example demonstrate how to load an EDF file.

Required dataset at :
https://drive.google.com/drive/folders/0B6vtJiCQZUBvRjc3cFFYcmFIeW8?usp=sharing

.. image:: ../../picture/picsleep/ex_LoadEDF.png
"""
from visbrain import Sleep

Sleep(file='excerpt2.edf', hypno_file='Hypnogram_excerpt2.txt',
      config_file='excerpt2_config.txt').show()
