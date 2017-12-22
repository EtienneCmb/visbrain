"""
Cross-sections and volume control
=================================

Control the cross-section panel and the volume. This script use a custom
nifti volume downloadable at : https://brainder.org/download/flair/
The nibabel package should also be installed.

.. image:: ../../picture/picbrain/ex_crossec_and_volume.png
"""
from visbrain import Brain
from visbrain.io import read_nifti, download_file

"""Import the volume and the associated affine transformation
"""
volume_name = 'GG-853-WM-0.7mm.nii.gz'

"""Download the file.
"""
data, header, tf = read_nifti(download_file(volume_name))

vb = Brain()

# Add the volume to the GUI
vb.add_volume(volume_name, data, transform=tf)

"""Set the cross-section to be centered on the slice (70, 171, 80) with the
gist_stern colormap.
"""
vb.cross_sections_control(center=(70, 171, 80), volume=volume_name,
                          cmap='gist_stern')

"""Display the 3D volume using the translucent rendering method.
"""
vb.volume_control(volume_name, cmap='TransFire', rendering='translucent')

"""Finally, rotate the scene and hide the main brain.
"""
vb.rotate(custom=(142, 12))
vb.brain_control(visible=False)

vb.show()
