"""
Animate objects in the scene
============================

This example illustrate how to animate objects inside the scene. Note that
animations can only be used with 3D objects.
"""
import numpy as np

from visbrain.objects import (BrainObj, SceneObj, SourceObj, ConnectObj)
from visbrain.io import download_file


###############################################################################
# Download data and create the scene
###############################################################################
# The SceneObj is Matplotlib subplot like in which, you can add visbrain's
# objects. We first create the scene with a black background, a fixed size

# Download intracranial EEG electodes
mat = np.load(download_file('xyz_sample.npz', astype='example_data'))
xyz, subjects = mat['xyz'], mat['subjects']
n_sources = xyz.shape[0]

# Generate random data and random connectivity
data = np.random.uniform(low=-1., high=1., size=(n_sources,))
conn = np.triu(np.random.uniform(-1., 1., (n_sources, n_sources)))
conn_select = (-.005 < conn) & (conn < .005)

# Scene creation
sc = SceneObj()


###############################################################################
# Animate a single brain object
###############################################################################
# Here we set an animation for a single brain object.

b_obj_1 = BrainObj('inflated', translucent=False)
b_obj_1.animate()
sc.add_to_subplot(b_obj_1, rotate='left', title='Animate a single object')

###############################################################################
# Animate multiple objects
###############################################################################
# Here we animate multiple objects inside a subplot

s_obj_1 = SourceObj('s1', xyz, data=data)
b_obj_2 = BrainObj('white')
b_obj_2.animate()

sc.add_to_subplot(s_obj_1, row=1, title='Animate multiple objects')
sc.add_to_subplot(b_obj_2, row=1, rotate='right', use_this_cam=True)


###############################################################################
# Animate sources
###############################################################################
# Previous subplots are using the brain object. But every 3D objects in
# Visbrain can also be animated. We illustrate this with a source object

# Define connectivity links and sources
c_obj_1 = ConnectObj('c1', xyz, conn, select=conn_select, dynamic=(0., 1.),
                     dynamic_orientation='center', dynamic_order=3, cmap='bwr',
                     antialias=True)
s_obj_2 = SourceObj('s2', xyz, data=data, radius_min=5., radius_max=20)
s_obj_2.color_sources(data=data, cmap='inferno')

# Animate sources
s_obj_2.animate()

# Add objects to the scene
sc.add_to_subplot(c_obj_1, col=1, title='Animate a source object')
sc.add_to_subplot(s_obj_2, col=1, rotate='front', use_this_cam=True, zoom=.7)

###############################################################################
# Configure the animation rate
###############################################################################
# Here, we configure animations so that there's a 60° rotation update every
# second

# Define a connectivity object and a brain object :
c_obj_2 = ConnectObj('c1', xyz, conn, select=conn_select, dynamic=(0., 1.),
                     dynamic_orientation='center', cmap='bwr', antialias=True)
b_obj_3 = BrainObj('white')

# Animate the brain with 10 iterations of 60° rotation update every second
b_obj_3.animate(iterations=10, step=60, interval=1)

# Add both objects to the scene and specify that we want to use the camera of
# the brain object
sc.add_to_subplot(c_obj_2, row=1, col=1,
                  title='1s refresh rate with a 60° rotation update')
sc.add_to_subplot(b_obj_3, row=1, col=1, rotate='front',
                  use_this_cam=True)


###############################################################################
# Save the animation
###############################################################################
# Finally, the `visbrain.objects.SceneObj.record_animation` allows to export
# animations as a gif file

# sc.record_animation('animate_example.gif', n_pic=10)

sc.preview()
