"""
Cross-section object
====================

Illustration and main functionalities and inputs of the cross-section object.

.. image:: ../../picture/picobjects/ex_cs_obj.png
"""
from visbrain.objects import CrossSecObj, SceneObj
from visbrain.io import download_file

sc = SceneObj()

print("""
# =============================================================================
#                              Brodmann area
# =============================================================================
""")
cs_brod = CrossSecObj('brodmann', interpolation='nearest',
                      coords=(70., 80., 90.))
cs_brod.localize_source((-10., -15., 20.))
sc.add_to_subplot(cs_brod, row=0, col=0, title='Brodmann area')

print("""
# =============================================================================
#                              Nii.gz file
# =============================================================================
""")
path = download_file('GG-853-GM-0.7mm.nii.gz', astype='example_data')
cs_cust = CrossSecObj(path, coords=(0., 0., 0.), cmap='gist_stern')
sc.add_to_subplot(cs_cust, row=0, col=1, title='Nii.gz file')

sc.preview()
