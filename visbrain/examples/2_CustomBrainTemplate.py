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
# So, we can add a transformation to correct the default rotation.

# Define a empty chain of transformations :
chain = vist.ChainTransform([])

# Define a rotation of 180° arround y axis :
rot2 = vist.MatrixTransform()
rot2.rotate(180, (0,1,0))
chain.append(rot2) # Add it the chain 

# Define an other rotation of 270° arround z axis :
rot1 = vist.MatrixTransform()
rot1.rotate(270, (0,0,1))
chain.append(rot1) # Add it the chain 

# Sometimes the brain appear to be full black. In that
# case, multiply each dimension with -1.
scale = vist.STTransform(scale=[-1, -1, -1])
chain.append(scale)

# Finally apply the transformation to vertices :
vert = chain.map(vert)[:, 0:-1]

vb = visbrain.vbrain(a_vertices=vert, a_faces=faces)

vb.show()