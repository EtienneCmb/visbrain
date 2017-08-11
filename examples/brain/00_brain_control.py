"""
Brain control
=============

This example basic brain controls such as the choice of the template to use,
the hemisphere to display and transparency level.
By default, Visbrain come with three different templates (B1, B2 and B3).

This file also show how to rotate the using either predefined rotations
(axial, sagittal or coronal) or custom rotation.

Fixed parameters for rotation :
* 'axial_0': top view
* 'axial_1': bottom view
* 'coronal_0': front
* 'coronal_1': back view
* 'sagittal_0': left view
* 'sagittal_1': right view

Custom rotation consist of a tuple of two floats repsectively for azimuth and
elevation.
"""
from visbrain import Brain

# Define the Brain instance :
vb = Brain()

# Display opaque B1 :
vb.brain_control(template='B1', transparent=False)

# Display tranparent right hemisphere of B3 :
# vb.brain_control(template='B3', hemisphere='right', alpha=.1)

# Fixed front view :
# vb.rotate(fixed='coronal_0')

# Display transparent left hemisphere of B2 :
# vb.brain_control(template='B2', hemisphere='left', alpha=.5)

# Custom rotation (azimuth=-34°, elevation=74°)
# vb.rotate(custom=(-34, 74))  # Custom rotation

vb.show()

