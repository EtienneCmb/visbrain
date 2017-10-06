"""
Load a BrainVision file
=======================

This example demonstrate how to load a BrainVision file.

Required dataset at :
https://www.dropbox.com/s/t2bo9ufvc3f8mbj/sleep_brainvision.zip?dl=1

.. image:: ../../picture/picsleep/ex_LoadBrainVision.png
"""
import os
from visbrain import Sleep
from visbrain.io import download_file

current_path = os.getcwd()
target_path = os.path.join(current_path, 'data', 'brainvision')

# Download dataset :
download_file("sleep_brainvision.zip", unzip=True, to_path=target_path)

dfile = os.path.join(target_path, 'sub-02.vhdr')
hfile = os.path.join(target_path, 'sub-02.hyp')
cfile = os.path.join(target_path, 'sub-02_config.txt')

Sleep(data=dfile, hypno=hfile, config_file=cfile).show()
