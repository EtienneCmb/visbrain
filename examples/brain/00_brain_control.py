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

    * Top view : 'top' or 'axial_0'
    * Bottom view : 'bottom' or 'axial_1'
    * Left : 'left' or 'sagittal_0'
    * Right : 'right' or 'sagittal_1'
    * Front : 'front' or 'coronal_0'
    * Back : 'back' or 'coronal_1'

Custom rotation consist of a tuple of two floats repsectively for azimuth and
elevation.

.. image:: ../../picture/picbrain/ex_brain_control.png
"""
from visbrain import Brain

# Define the Brain instance :
vb = Brain()

"""
Display opaque right hemisphere of B3 :
"""
# vb.brain_control(template='B3', hemisphere='right', translucent=False)

"""
Fixed frontal view
"""
# vb.rotate(fixed='front')

"""
Display transparent left hemisphere of B2
"""
# vb.brain_control(template='B2', hemisphere='left', alpha=.05)

"""
Custom rotation
    * azimuth = -34°
    * elevation = 74°
"""
# vb.rotate(custom=(-34, 74))  # Custom rotation

"""
Hide the brain
"""
# vb.brain_control(visible=False)

"""
Change background color
"""
# vb.background_color('#34495e')

vb.show()
