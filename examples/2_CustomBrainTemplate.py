"""This example demonstrate how to import a custom atlas and to adapt it
to the software.
"""
import visbrain
import os
import numpy as np
import vispy.visuals.transforms as vist

# Define path and filename of the template :
path = os.path.dirname(visbrain.__file__)+'/examples/'
file = 'custom_template.npz'

# Get faces/vertices :
mat = np.load(path+file)
vert, faces = mat['coord'], mat['tri']

# By default, this template is rotated (compared to default templates in visbrain)
# So, we can add a transformation to correct the default rotation. We are going
# to rotate about 90° around the z axis :
trans = vist.MatrixTransform()
trans.rotate(90, (0,0,1))

vb = visbrain.vbrain(a_vertices=vert, a_faces=faces, t_transform=trans)

vb.show()