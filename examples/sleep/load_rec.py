"""
Load REC files
==============

This example demonstrate how to load a .rec file.

Required dataset at :
https://www.dropbox.com/s/hc18bgn2hlnmiph/sleep_edf.zip?dl=1
"""
import os

from visbrain import Sleep
from visbrain.io import download_file, path_to_visbrain_data

###############################################################################
#                               LOAD YOUR FILE
###############################################################################
current_path = path_to_visbrain_data()
target_path = os.path.join(current_path, 'sleep_data', 'rec')

# Download the rec file :
download_file('sleep_rec.zip', unzip=True, to_path=target_path,
              remove_archive=True)

dfile = os.path.join(target_path, '1.rec')

# Open the GUI :
Sleep(data=dfile).show()
