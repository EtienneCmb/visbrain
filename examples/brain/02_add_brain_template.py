"""
Add a brain template
====================

This example illustrate how to add a template to the interface.

As an example, download the WhiteMatter.npz file :
https://drive.google.com/open?id=0B6vtJiCQZUBvd0xfTHJqcHg2bTA
"""
from __future__ import print_function
import os

import numpy as np

from visbrain import Brain
from visbrain.utils import (add_brain_template, remove_brain_template)

# Define path to the template and load it :
path_to_file = os.path.join(*(os.getenv("HOME"), 'Templates',
                              'WhiteMatter.npz'))
mat = np.load(path_to_file)

# Get vertices, faces and normals from the archive :
vert, faces, norm = mat['vertices'], mat['faces'], mat['normals']

# Add the template :
add_brain_template('WhiteMatter', vert, faces, norm)

vb = Brain(a_template='Custom')
print('Brain templates : ', vb.brain_list())
vb.show()

# If you want to remove the template :
remove_brain_template('Custom')
