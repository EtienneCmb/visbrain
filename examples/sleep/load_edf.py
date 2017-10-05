"""
Load EDF file
=============

This example demonstrate how to load an EDF file.

Required dataset at :
https://www.dropbox.com/s/bj1ra95rbksukro/sleep_edf.zip?dl=1

.. image:: ../../picture/picsleep/ex_LoadEDF.png
"""
import os
from visbrain import Sleep
from visbrain.io import download_file

current_path = os.getcwd()
target_path = os.path.join(current_path, 'data', 'edf')

download_file('sleep_edf.zip', unzip=True, to_path=target_path)

dfile = os.path.join(target_path, 'excerpt2.edf')
hfile = os.path.join(target_path, 'Hypnogram_excerpt2.txt')
cfile = os.path.join(target_path, 'excerpt2_config.txt')

Sleep(data=dfile, hypno=hfile, config_file=cfile).show()
