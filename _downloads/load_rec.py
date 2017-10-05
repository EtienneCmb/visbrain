"""
Load REC files
==============

This example demonstrate how to load a .rec file.

Required dataset at :
https://www.dropbox.com/s/hc18bgn2hlnmiph/sleep_edf.zip?dl=1
"""

from visbrain import Sleep
from visbrain.io import download_file

# Download the rec file :
download_file('sleep_rec.zip', unzip=True)

Sleep(data='1.rec').show()
