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

"""
Define path to the template and load it. By default, the path is set to
~/home/Templates/ so you have to adapt it.
"""
path_to_file = os.path.join(*(os.getenv("HOME"), 'Templates',
                              'WhiteMatter.npz'))
mat = np.load(path_to_file)

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
add_brain_template('WhiteMatter', vert, faces, norm, lr_index)

"""
Open the interface and select the added template
"""
vb = Brain(a_template='WhiteMatter')
print('Brain templates : ', vb.brain_list())
vb.show()

"""
Finally, and this is not a necessity, remove the template
"""
remove_brain_template('WhiteMatter')
