"""
Add Nifti volume
================

Import a custom Nifti volume that can be then used in the cross-section or
volume tab. To this end, the python package nibabel must be installed and
custom Nifti volume must be downloaded.
When the volume is loaded into the GUI, it's accessible from the
Brain/Cross-sections and Brain/Volume tab.

This script use a custom nifti volume downloadable at :
https://brainder.org/download/flair/

.. image:: ../../picture/picbrain/ex_add_nifti.png
"""
from __future__ import print_function
import numpy as np
import os

from visbrain import Brain
from visbrain.io import read_nifti

# Define four sources sources :
s_xyz = np.array([[29.9, -37.3, -19.3],
                  [-5.33, 14.00, 20.00],
                  [25.99, 14.00, 34.66],
                  [0., -1.99, 10.66]])

# Define a Brain instance :
vb = Brain(s_xyz=s_xyz)

# Print the list of volumes available :
print('Volumes available by default : ', vb.volume_list())

"""
If you don't have access to a Nifti file, download one of the volume available
at https://brainder.org/download/flair/.
"""
path_to_nifti1 = os.getenv("HOME")       # Path to the Nifti file
file_nifti1 = 'GG-853-GM-0.7mm.nii.gz'   # Name of the Nifti file
path1 = os.path.join(path_to_nifti1, file_nifti1)

"""
Load the Nifti file. The read_nifti function load the data and the
transformation to convert data into the MNI space :
"""
data1, header1, tf1 = read_nifti(path1)
# print(header1)

# Add the volume to the GUI :
vb.add_volume('Volume1', data1, transform=tf1)
print('Add Volume1 to the list of volumes : ', vb.volume_list())

# You can add multiple volumes :
path_to_nifti2 = os.getenv("HOME")
file_nifti2 = 'GG-853-WM-0.7mm.nii.gz'
path2 = os.path.join(path_to_nifti2, file_nifti2)
data2, header2, tf2 = read_nifti(path2)
vb.add_volume('Volume2', data2, transform=tf2)
print('Add Volume2 to the list of volumes : ', vb.volume_list())

# Set the cross-section to be centered on the last source :
vb.cross_sections_control(pos=s_xyz[3, :], volume='Volume2', cmap='gist_stern',
                          split_view=True)

vb.show()
