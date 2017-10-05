"""
Load REC files
==============

This example demonstrate how to load a .rec file.
"""

from visbrain import Sleep
from visbrain.io import download_file

# Download the rec file :
download_file('sleep_rec.rec', unzip=True)

Sleep(data='sleep_rec.rec').show()
