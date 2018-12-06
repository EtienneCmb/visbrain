"""
Brain control
=============

Control the brain i.e the brain template to use, the transparency and
the hemisphere.

You can also rotate the scene using predefined rotations (axial, sagittal or
coronal) or custom rotation.

Fixed parameters for rotation :

    * Top view : 'top' or 'axial_0'
    * Bottom view : 'bottom' or 'axial_1'
    * Left : 'left' or 'sagittal_0'
    * Right : 'right' or 'sagittal_1'
    * Front : 'front' or 'coronal_0'
    * Back : 'back' or 'coronal_1'

Custom rotation consist of a tuple of two floats repsectively for azimuth and
elevation.

.. image:: ../../_static/examples/ex_brain_control.png
"""
from visbrain.gui import Brain
from visbrain.objects import BrainObj

"""Visbrain comes with three default templates :
* B1 (with cerebellum)
* B2
* B3

Three templates can also be downloaded :
* inflated (inflated brain of PySurfer)
* white
* sphere
"""
b_obj = BrainObj('B3')  # 'B1', 'B2', 'inflated', 'sphere', 'white'

"""By default, the brain is translucent but it can be turned to opaque
"""
# b_obj = BrainObj('B3', translucent=False)

"""You can also select a specific hemisphere
"""
# b_obj = BrainObj('B3', translucent=False, hemisphere='left')  # 'right'

"""For the inflated, white and translucent templates, sulcus can be also used
"""
# b_obj = BrainObj('inflated', translucent=False, hemisphere='right',
#                  sulcus=True)

"""Once the brain object created, pass it to the graphical user interface.

If you want to control the brain from the GUI, go to the Objects tab and select
'Brain' from the first combo box. You can also use the key shortcut b to
display/hide the brain.
"""
vb = Brain(brain_obj=b_obj, bgcolor='slateblue')

"""Display opaque right hemisphere of B3 :
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
