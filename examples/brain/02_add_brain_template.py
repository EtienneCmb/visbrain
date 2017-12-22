"""
Add a brain template
====================

Add a new brain template to the interface.

As an example, download the white.npz file :
https://drive.google.com/open?id=0B6vtJiCQZUBvd0xfTHJqcHg2bTA

.. image:: ../../picture/picbrain/ex_add_brain_template.png
"""
from __future__ import print_function

import numpy as np

from visbrain import Brain
from visbrain.objects import BrainObj
from visbrain.io import download_file

"""Download the brain template. Use either 'white', 'inflated' or 'sphere'
"""
template = 'white'
mat = np.load(download_file(template + '.npz'))

"""
Get variables for defining a new template. Vertices are nodes connected by the
faces variable. Normals are vectors orthogonal to each normals (used for light
adaptation according to camera rotations). lr_index is an array of boolean
values which specify where are the left and right hemispheres. This variable
can be set to None.
"""
vert, faces, norm = mat['vertices'], mat['faces'], mat['normals']
lr_index = mat['lr_index']

"""Define a brain object instance
"""
b_obj = BrainObj('NewWhite', vertices=vert, faces=faces, normals=norm,
                 lr_index=lr_index)

"""
Add the template to visbrain. After adding this template, it will always be
accessible unless you use the remove() method
"""
# b_obj.save()

"""
Open the interface and select the added template
"""
vb = Brain(brain_obj=b_obj)
vb.show()

"""
Finally, and this is not a necessity, remove the template
"""
# b_obj.remove()
