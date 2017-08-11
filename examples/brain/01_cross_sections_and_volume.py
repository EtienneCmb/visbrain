"""
Cross-sections and volume control
=================================

Customize the GUI.
"""
import os
from visbrain import Brain
from visbrain.io import read_nifti

# You can add multiple volumes :
path_to_nifti2 = os.getenv("HOME")
file_nifti2 = 'GG-853-WM-0.7mm.nii.gz'
path2 = os.path.join(path_to_nifti2, file_nifti2)
data2, header2, tf2 = read_nifti(path2)

# 142, 12

vb = Brain()
vb.add_volume('Volume2', data2, transform=tf2)
# vb.cross_sections_control(center=(70, 171, 80), volume='Volume2',
#                           cmap='gist_stern')

vb.volume_control('Volume2', cmap='TransFire', rendering='iso', threshold=.1)

vb.rotate(custom=(142, 12))
vb.brain_control(visible=False)
vb.show()
