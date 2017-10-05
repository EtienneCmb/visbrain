"""
Load a BrainVision file
=======================

This example demonstrate how to load a BrainVision file.

Required dataset at :
https://www.dropbox.com/s/t1s4e39gu3wdb6i/sleep_brainvision.zip?dl=0

.. image:: ../../picture/picsleep/ex_LoadBrainVision.png
"""
from visbrain import Sleep
from visbrain.io import download_file

# Download dataset :
download_file("sleep_brainvision.zip", unzip=True)

Sleep(data='sub-02.vhdr', hypno='sub-02.hyp').show()
