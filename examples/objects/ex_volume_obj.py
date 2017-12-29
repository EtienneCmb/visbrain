"""
Volume object
=============

Illustration of the main functionalities and inputs of the volume object.

.. image:: ../../picture/picobjects/ex_vol_obj.png
"""
from visbrain.objects import VolumeObj, SceneObj
from visbrain.io import download_file


sc = SceneObj()

print("""
# =============================================================================
#                              MIP rendering
# =============================================================================
""")
v_obj_mip = VolumeObj('brodmann', method='mip', cmap='OpaqueFire')
sc.add_to_subplot(v_obj_mip, row=0, col=0, title='MIP rendering')

print("""
# =============================================================================
#                              Translucent rendering
# =============================================================================
""")
v_obj_trans = VolumeObj('aal', method='translucent', cmap='TransFire')
sc.add_to_subplot(v_obj_trans, row=0, col=1, title='Translucent rendering')

print("""
# =============================================================================
#                              Additive rendering
# =============================================================================
""")
v_obj_add = VolumeObj('talairach', method='additive', cmap='TransGrays')
sc.add_to_subplot(v_obj_add, row=0, col=2, title='Additive rendering')

print("""
# =============================================================================
#                                Iso rendering
# =============================================================================
""")
v_obj_iso = VolumeObj('brodmann', method='iso', cmap='OpaqueFire')
sc.add_to_subplot(v_obj_iso, row=0, col=3, title='Iso rendering')

print("""
# =============================================================================
#                                 Select ROI
# =============================================================================
""")
v_obj_select = VolumeObj('brodmann', method='iso', cmap='OpaqueFire',
                         select=[4, 6])
sc.add_to_subplot(v_obj_select, row=1, col=0,
                  title='Select Brodmann area 4 and 6')


print("""
# =============================================================================
#                              Custom nii.gz file
# =============================================================================
""")
path = download_file('GG-853-GM-0.7mm.nii.gz')
v_obj_nii = VolumeObj(path, method='mip', cmap='OpaqueGrays', threshold=.7)
sc.add_to_subplot(v_obj_nii, row=1, col=1, title='Custom nii.gz file')


print("""
# =============================================================================
#                              Second nii.gz file
# =============================================================================
""")
path = download_file('GG-853-WM-0.7mm.nii.gz')
vol_obj_sec = VolumeObj(path, method='translucent', cmap='TransGrays')
sc.add_to_subplot(vol_obj_sec, row=1, col=2, title='Second nii.gz file')

print("""
# =============================================================================
#                              Threshold selection
# =============================================================================
""")
path = download_file('GG-853-WM-0.7mm.nii.gz')
vol_obj_th = VolumeObj(path, method='iso', threshold=.1)
sc.add_to_subplot(vol_obj_th, row=1, col=3, title='Threshold selection')


sc.preview()