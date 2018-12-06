"""
Volume object (VolumeObj) : complete tutorial
=============================================

Illustration of the main functionalities and inputs of the volume object :

    * Volume rendering methods (MIP, translucent, additive, Iso)
    * Colormap choice
    * Select volume levels
    * Load an MRI (nii.gz) file
"""
from visbrain.objects import VolumeObj, SceneObj
from visbrain.io import download_file


# Define the scene
sc = SceneObj(size=(1000, 600))

###############################################################################
# MIP rendering
###############################################################################
# MIP rendering with an opaque fire colormap

v_obj_mip = VolumeObj('brodmann', method='mip', cmap='OpaqueFire')
sc.add_to_subplot(v_obj_mip, row=0, col=0, title='MIP rendering', zoom=.7)

###############################################################################
# Translucent rendering
###############################################################################
# Translucent rendering with a translucent fire colormap

v_obj_trans = VolumeObj('aal', method='translucent', cmap='TransFire')
sc.add_to_subplot(v_obj_trans, row=0, col=1, title='Translucent rendering',
                  zoom=.7)

###############################################################################
# Additive rendering
###############################################################################
# Additive rendering with a translucent grays colormap

v_obj_add = VolumeObj('talairach', method='additive', cmap='TransGrays')
sc.add_to_subplot(v_obj_add, row=0, col=2, title='Additive rendering', zoom=.6)

###############################################################################
# Iso rendering
###############################################################################
# Iso rendering. Note that here, no threshold are used

v_obj_iso = VolumeObj('brodmann', method='iso')
sc.add_to_subplot(v_obj_iso, row=0, col=3, title='Iso rendering', zoom=.7)

###############################################################################
# Volume thresholding
###############################################################################
# Similarly to the example above, here, we use a threshold to cut the volume

path = download_file('GG-853-WM-0.7mm.nii.gz', astype='example_data')
vol_obj_th = VolumeObj(path, method='iso', threshold=.1)
sc.add_to_subplot(vol_obj_th, row=1, col=0, title='Threshold selection',
                  zoom=.7)

###############################################################################
# Select volume levels
###############################################################################
# The volume contains certain levels and you can use the `select` input to
# select only certain levels

v_obj_select = VolumeObj('brodmann', method='iso', cmap='OpaqueFire',
                         select=[4, 6])
sc.add_to_subplot(v_obj_select, row=1, col=1, zoom=.7,
                  title='Select Brodmann area 4 and 6')

###############################################################################
# MRI file : mip rendering
###############################################################################

path = download_file('GG-853-GM-0.7mm.nii.gz', astype='example_data')
v_obj_nii = VolumeObj(path, method='mip', cmap='OpaqueGrays', threshold=.7)
sc.add_to_subplot(v_obj_nii, row=1, col=2, title='MRI file (MIP rendering)',
                  zoom=.7)

###############################################################################
# MRI file : translucent rendering
###############################################################################

path = download_file('GG-853-WM-0.7mm.nii.gz', astype='example_data')
vol_obj_sec = VolumeObj(path, method='translucent', cmap='TransGrays')
sc.add_to_subplot(vol_obj_sec, row=1, col=3, zoom=.7,
                  title='MRI file (translucent rendering)')

# Finally, display the scene
sc.preview()
