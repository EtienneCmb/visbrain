"""
Cross-sections and volume control
=================================

Control the cross-section panel and the volume. This script use a custom
nifti volume downloadable at : https://brainder.org/download/flair/
The nibabel package should also be installed.

.. image:: ../../picture/picbrain/ex_crossec_and_volume.png
"""
from visbrain import Brain
from visbrain.objects import CrossSecObj, VolumeObj
from visbrain.io import download_file

"""Import the volume and the associated affine transformation
"""
volume_name = 'GG-853-WM-0.7mm.nii.gz'

"""Download the file.
"""
path = download_file(volume_name)

"""Define a cross-section object
"""
cs_obj = CrossSecObj(path, section=(70, 171, 80), cmap='gist_stern')
v_obj = VolumeObj(path)

vb = Brain(cross_sec_obj=cs_obj, vol_obj=v_obj)
vb.show()
