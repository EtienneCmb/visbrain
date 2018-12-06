"""
Add vectors
===========

Add vectors to the scene. This example demonstrate the two methods to defined
vectors :

    * By defining for each vector where it start and finish
    * Using the normals to the vertices;

Download source's coordinates (xyz_sample.npz) :
https://www.dropbox.com/s/whogfxutyxoir1t/xyz_sample.npz?dl=1

.. image:: ../../_static/examples/ex_vectors.png
"""
import numpy as np

from visbrain.gui import Brain
from visbrain.objects import VectorObj, BrainObj, SourceObj
from visbrain.io import download_file

kwargs = {}

"""
Load the xyz coordinates and corresponding subject name
"""
mat = np.load(download_file('xyz_sample.npz', astype='example_data'))
xyz, subjects = mat['xyz'], mat['subjects']

"""The first vector object use the position of a subset of sources as a
starting point. The end point of each arrow is defined as 1.3 further where the
arrow start.
"""
sl_1 = slice(60, 80)           # Subset of sources
arrow_start = xyz[sl_1, :]     # Positions of each arrow start
arrow_end = 1.3 * arrow_start  # Position of the end of each arrow
data = xyz[sl_1, 0]            # Data attached to each vctor

v_obj1 = VectorObj('v1', [arrow_start, arrow_end], data=data,
                   antialias=True, arrow_size=6., line_width=6.,
                   arrow_type='triangle_60')
s_obj = SourceObj('s1', xyz[sl_1, :], color='white', data=data, radius_min=10.)

"""The second vector object is the symetric of the first one but this time the
data are inferred from the norm of each vector.
"""
v_obj2 = VectorObj('v2', [-arrow_start, -arrow_end], inferred_data=True,
                   line_width=3., arrow_size=6., arrow_type='angle_90',
                   antialias=True, cmap='inferno')
s_obj2 = SourceObj('s2', -xyz[sl_1, :], color='red', radius_min=10)


"""Finally, the last vector object is defined using the vertices and the
normals of the right hemisphere of the brain.
"""
b_obj = BrainObj('B2', hemisphere='right')  # Define the brain object
n = len(b_obj)                              # Get the number of vertices

dtype = [('vertices', float, 3), ('normals', float, 3)]  # Arrows dtype
arrows = np.zeros(n, dtype=dtype)                        # Empty arrows array
arrows['vertices'] = b_obj.vertices                      # Set the vertices
arrows['normals'] = b_obj.normals                        # Set the normals

# For the data, we use the distance between 0 and each vertex
data = np.linalg.norm(b_obj.vertices, axis=1)
# We only select vectors with a distance in [60., 60.2]
select = np.logical_and(data >= 60., data <= 60.2)

v_obj3 = VectorObj('v3', arrows, data=data, select=select, line_width=2.,
                   arrow_size=7., arrow_type='inhibitor_round', antialias=True,
                   cmap='Spectral_r', vmin=60.05, under='gray')
# Finally, re-select both brain hemispheres.
b_obj.hemisphere = 'both'

vb = Brain(brain_obj=b_obj, vector_obj=[v_obj1, v_obj2, v_obj3],
           source_obj=[s_obj, s_obj2])
vb.show()
