"""
Brain control
=============

Control the brain such as the choice of the template to use, the hemisphere
to display and transparency level. By default, Visbrain come with three
different templates (B1, B2 and B3).

This file also show how to rotate the using either predefined rotations
(axial, sagittal or coronal) or custom rotation. Uncomment lines to be
executed.

Fixed parameters for rotation :

    * 'axial_0': top view
    * 'axial_1': bottom view
    * 'coronal_0': front
    * 'coronal_1': back view
    * 'sagittal_0': left view
    * 'sagittal_1': right view

Custom rotation consist of a tuple of two floats repsectively for azimuth and
elevation.

.. image:: ../../picture/picbrain/ex_brain_control.png
"""
from visbrain import Brain

# Define the Brain instance :
vb = Brain()

"""
Display opaque B1 :
"""
# vb.brain_control(template='B1', transparent=False)

"""
Display tranparent right hemisphere of B3 :
"""
# vb.brain_control(template='B3', hemisphere='right', alpha=.1)

"""
Fixed frontal view
"""
# vb.rotate(fixed='coronal_0')

"""
Display transparent left hemisphere of B2
"""
# vb.brain_control(template='B2', hemisphere='left', alpha=.5)

"""
Custom rotation
    * azimuth=-34°
    * elevation=74°
"""
# vb.rotate(custom=(-34, 74))  # Custom rotation

"""
Hide the brain
"""
# vb.brain_control(visible=False)

"""
Change the color of the brain. You define three colors using :
    * Matplotlib colors ('red', 'white', 'slateblue'...)
    * RGB tuple ((1., 0., 0.), (1., 1., 1.)...)
    # Hexadecimal ('#ab4642'...)
"""
# vb.brain_control(color=(0.9, 0.29, 0.24))

"""
Change background color
"""
# vb.background_color('#34495e')

vb.show()
