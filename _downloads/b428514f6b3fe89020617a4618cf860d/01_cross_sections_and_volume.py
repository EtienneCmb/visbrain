"""
Cross-sections and volume control
=================================

Control the cross-section panel and the volume using a Nifti file. The nibabel
package should also be installed.

See : https://brainder.org/download/flair/

.. image:: ../../_static/examples/ex_crossec_and_volume.png
"""
from visbrain.gui import Brain
from visbrain.objects import CrossSecObj, VolumeObj
from visbrain.io import download_file

"""Import the volume and the associated affine transformation
"""
volume_name = 'GG-853-WM-0.7mm.nii.gz'  # 'GG-853-GM-0.7mm.nii.gz'

"""Download the file.
"""
path = download_file(volume_name, astype='example_data')

"""Define a cross-section object

Go to the Objects tab and select 'Cross-section' in the combo box. You can also
press x to display the cross-section panel.
"""
cs_obj = CrossSecObj(path, coords=(0., 0., 0.), cmap='gist_stern')

"""Define a volume object.

Go to the Objects tab and select 'Volume' in the combo box. You can also
press x to display the volume panel.
"""
v_obj = VolumeObj(path)

"""Create the GUI and pass the cross-section and the volume object
"""
vb = Brain(cross_sec_obj=cs_obj, vol_obj=v_obj)
vb.show()
