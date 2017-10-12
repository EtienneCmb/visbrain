"""
Convert mesh data
=================

This example illustrate how to convert mesh data to be compatible with
visbrain.

As an example, download the Custom.npz file :
https://www.dropbox.com/s/phzptkbht4us33q/Custom.npz?dl=1

.. image:: ../../picture/picbrain/ex_convert_mesh_data.png
"""
import numpy as np
import vispy.visuals.transforms as vist

from visbrain import Brain
from visbrain.utils import (convert_meshdata, add_brain_template,
                            remove_brain_template)
from visbrain.io import download_file, path_to_visbrain_data

# Define path to the template and load it :
download_file(path_to_visbrain_data('Custom.npz'))
mat = np.load('Custom.npz')

# Get vertices and faces from the archive :
vert, faces = mat['coord'], mat['tri']

# By default the template is not correctly oriented and need a 90° rotation.
# To this end, we define a rotation using VisPy :
z90_rotation = vist.MatrixTransform()
z90_rotation.rotate(90, (0, 0, 1))

# Then we extract vertices, faces and normals. By default, normals of this
# template are not correclty oriented so we the invert_normals to True :
vertices, faces, normals = convert_meshdata(vert, faces, invert_normals=True,
                                            transform=z90_rotation)

# Add the template :
add_brain_template('Custom', vertices, faces, normals)

vb = Brain(a_template='Custom')
vb.show()

# If you want to remove the template :
remove_brain_template('Custom')
