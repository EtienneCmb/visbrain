"""
Load ELAN files
===============

This example demonstrate how to load an ELAN file.

Required dataset at :
https://www.dropbox.com/s/95xvdqivpgk90hg/sleep_elan.zip?dl=1

.. image:: ../../picture/picsleep/ex_LoadElan.png
"""
import os
from visbrain import Sleep
from visbrain.io import download_file

current_path = os.getcwd()
target_path = os.path.join(current_path, 'data', 'elan')

# Download dataset :
download_file("sleep_elan.zip", unzip=True, to_path=target_path)

dfile = os.path.join(target_path, 'sub-02.eeg')
hfile = os.path.join(target_path, 'sub-02.hyp')

Sleep(data=dfile, hypno=hfile).show()
