"""
Load a BrainVision file
=======================

This example demonstrate how to load a BrainVision file.

Required dataset at :
https://drive.google.com/drive/folders/0B6vtJiCQZUBvRjc3cFFYcmFIeW8?usp=sharing

.. image:: ../../picture/picsleep/ex_LoadBrainVision.png
"""
from visbrain import Sleep

Sleep(file='sub-02.eeg', hypno_file='sub-02.hyp',
      config_file='sub-02_config.txt').show()
