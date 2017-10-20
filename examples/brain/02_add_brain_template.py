"""
Add a brain template
====================

Add a new brain template to the interface.

As an example, download the WhiteMatter.npz file :
https://drive.google.com/open?id=0B6vtJiCQZUBvd0xfTHJqcHg2bTA

.. image:: ../../picture/picbrain/ex_add_brain_template.png
"""
from __future__ import print_function
import os

import numpy as np

from visbrain import Brain
from visbrain.utils import (add_brain_template, remove_brain_template)
from visbrain.io import download_file, path_to_visbrain_data

"""Download the brain template. Use either 'WhiteMatter', 'Inflated' or
'Sphere'
"""
template = 'WhiteMatter'
download_file(template + '.npz')
mat = np.load(path_to_visbrain_data(template + '.npz'))

"""
Get variables for defining a new template. Vertices are nodes connected by the
faces variable. Normals are vectors orthogonal to each normals (used for light
adaptation according to camera rotations). lr_index is an array of boolean
values which specify where are the left and right hemispheres. This variable
can be set to None.
"""
vert, faces, norm = mat['vertices'], mat['faces'], mat['normals']
lr_index = mat['lr_index']

"""
Add the template to visbrain. After adding this template, it will always be
accessible unless you use the remove_brain_template() function
"""
add_brain_template(template, vert, faces, norm, lr_index)

"""
Open the interface and select the added template
"""
vb = Brain(a_template=template)
print('Brain templates : ', vb.brain_list())
vb.show()

"""
Finally, and this is not a necessity, remove the template
"""
remove_brain_template(template)
