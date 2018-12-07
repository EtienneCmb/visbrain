"""
Define a brain template using vertices and faces
================================================

This example illustrate how to define a custom brain template using your own
vertices and faces.

.. image:: ../../_static/examples/ex_add_brain_template.png
"""
import numpy as np

from visbrain.gui import Brain
from visbrain.objects import BrainObj
from visbrain.io import download_file

"""Download and the load the Custom.npz archive. This file contains vertices
and faces of a brain template that is not integrated by default in Visbrain.
"""
mat = np.load(download_file('Custom.npz', astype='example_data'))

"""Get vertices and faces from the archive.

In this examples, normals are also present in the archive. If you don't have
the normals, the BrainObj will compute it automatically.
"""
vert, faces, norms = mat['vertices'], mat['faces'], mat['normals']

"""Define the brain object
"""
b_obj = BrainObj('Custom', vertices=vert, faces=faces, normals=norms)

"""Then you have two strategies :
* If you are going to use this template a lot and don't want to redefine it
  every times, use `b_obj.save()`. Once the object saved, it can be reloaded
  using its name only `BrainObj('Custom')`
* If you only need it once, the template is temporaly saved and remove once the
  GUI is closed.
"""
# b_obj.save()
# b_obj = BrainObj('Custom')

"""Define the GUI and pass the brain template
"""
vb = Brain(brain_obj=b_obj)
vb.show()

# If you want to remove the template :
# b_obj.remove()
