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

.. image:: ../../_static/examples/ex_add_nifti.png
"""
from __future__ import print_function
import numpy as np

from visbrain.gui import Brain
from visbrain.objects import VolumeObj, CrossSecObj, SourceObj
from visbrain.io import download_file

"""Download two NIFTI files
"""
path_1 = download_file('GG-853-GM-0.7mm.nii.gz', astype='example_data')
path_2 = download_file('GG-853-WM-0.7mm.nii.gz', astype='example_data')

"""Define four sources sources and a Source object
"""
s_xyz = np.array([[29.9, -37.3, -19.3],
                  [-5.33, 14.00, 20.00],
                  [25.99, 14.00, 34.66],
                  [0., -1.99, 10.66]])
s_obj = SourceObj('MySources', s_xyz)

"""Define a volume object and a cross-section object
"""
vol_obj = VolumeObj(path_1)
cross_sec_obj = CrossSecObj(path_2)

"""Localize a source in the cross-section object
"""
cross_sec_obj.localize_source(s_xyz[2, :])

"""Define a Brain instance and pass the source, volume and cross-section
object
"""
vb = Brain(source_obj=s_obj, vol_obj=vol_obj, cross_sec_obj=cross_sec_obj)
vb.show()
