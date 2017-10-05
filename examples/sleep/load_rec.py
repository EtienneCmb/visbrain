"""
Load REC files
==============

This example demonstrate how to load a .rec file.

Required dataset at :
https://www.dropbox.com/s/hc18bgn2hlnmiph/sleep_edf.zip?dl=1
"""

from visbrain import Sleep
from visbrain.io import download_file
import os

current_path = os.getcwd()
target_path = os.path.join(current_path, 'data', 'rec')

# Download the rec file :
download_file('sleep_rec.zip', unzip=True, to_path=target_path, remove_archive=True)

dfile = os.path.join(target_path, '1.rec')

Sleep(data=dfile).show()
