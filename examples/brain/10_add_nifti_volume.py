"""
Add Nifti volume
================

This example demonstrate how to use a custom Nifti volume. To this end, the
python package nibabel must be installed and custom Nifti volume must be
downloaded.
When the volume is loaded into the GUI, it's accessible from the
Brain/Cross-sections and Brain/Volume tab.
"""
import os

from visbrain import Brain
from visbrain.io import read_nifti

# Define a Brain instance :
vb = Brain()

# If you don't have access to a Nifti file, download one of the volume avaible
# at https://brainder.org/download/flair/.
path_to_nifti1 = os.getenv("HOME")       # Path to the Nifti file
file_nifti1 = 'GG-853-GM-0.7mm.nii.gz'   # Name of the Nifti file
path1 = os.path.join(path_to_nifti1, file_nifti1)

# Load the Nifti file. The read_nifti function load the data and the
# transformation to convert data into the MNI space :
data1, header1, tf1 = read_nifti(path1)
# print(header1)

# Add the volume to the GUI :
vb.add_volume('Volume1', data1, transform=tf1)

# You can add multiple volumes :
path_to_nifti2 = os.getenv("HOME")
file_nifti2 = 'GG-853-WM-0.7mm.nii.gz'
path2 = os.path.join(path_to_nifti2, file_nifti2)
data2, header2, tf2 = read_nifti(path2)
vb.add_volume('Volume2', data2, transform=tf2)

vb.show()
