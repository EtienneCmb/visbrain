"""
Load ELAN files
===============

This example demonstrate how to load an ELAN file.

Required dataset at :
https://drive.google.com/drive/folders/0B6vtJiCQZUBvRjc3cFFYcmFIeW8?usp=sharing

.. image:: ../../picture/picsleep/ex_LoadElan.png
"""
from visbrain import Sleep
Sleep(file='s101_sleep.eeg', hypno_file='s101_hypno.hyp',
      config_file='s101_config.txt').show()
