"""
Add multiple objects to the scene
=================================

This example demonstrate how to display connectivity. To this end,
we will define some deep sources and connect them. See 2_Sources.py
to defined sources

Download source's coordinates (xyz_sample.npz) :
https://drive.google.com/open?id=0B6vtJiCQZUBvSFJvaTFSRDJvMEE

.. image:: ../../picture/picbrain/ex_add_multiple_objects.png
"""
from __future__ import print_function
from visbrain import Brain
import numpy as np

# Create an empty kwargs dictionnary :
kwargs = {}

# Load the xyz coordinates and corresponding subject name :
mat = np.load('xyz_sample.npz')
s_xyz, subjects = mat['xyz'], mat['subjects']

# Separate source's coodinates : in this part, first we find where sources
# are in the left hemisphere, then in the right hemisphere and in front and
# finally right hemisphere back :
s_xyzL = s_xyz[s_xyz[:, 0] <= 0, :]
s_xyzRB = s_xyz[np.logical_and(s_xyz[:, 0] > 0, s_xyz[:, 1] <= 0), :]
s_xyzRF = s_xyz[np.logical_and(s_xyz[:, 0] > 0, s_xyz[:, 1] > 0), :]

# Function in order to create random connection dataset for each
# source object :


def create_connect(xyz, min, max):
    """Create connectivity dataset."""
    # Create a random connection dataset :
    connect = 100. * np.random.rand(len(xyz), len(xyz))
    # Mask the connection aray :
    connect = np.ma.masked_array(connect, False)
    # Hide lower triangle :
    connect.mask[np.tril_indices_from(connect.mask)] = True
    # Hide connexions that are not between min and max :
    connect.mask[np.logical_or(connect.data < min,
                               connect.data > max)] = True
    return connect


vb = Brain()


# ================ ADD SOURCE OBJECTS ================
# Add left hemisphere sources :
vb.add_sources('sources_L', s_xyz=s_xyzL, s_symbol='disc',
               s_color='#ab4642', s_edgecolor='black', s_scaling=True,
               s_data=np.random.normal(size=len(s_xyzL)), s_radiusmin=1.,
               s_radiusmax=10., s_opacity=.5)

# Add right / front sources :
vb.add_sources('sources_RF', s_xyz=s_xyzRF, s_symbol='square',
               s_color='gray', s_data=np.random.normal(size=len(s_xyzRF)),
               s_radiusmin=3., s_radiusmax=7., s_opacity=.1)

# Add right / back sources :
vb.add_sources('sources_RB', s_xyz=s_xyzRB, s_symbol='x',
               s_color='orange', s_edgewidth=0., s_scaling=True,
               s_data=np.random.normal(size=len(s_xyzRB)),
               s_radiusmin=3., s_radiusmax=5., s_opacity=.7)

# ================ ADD CONNECTIVITY OBJECTS ================
# Add left hemisphere connectivity :
connectL = create_connect(s_xyzL, 0., 0.5)
vb.add_connect('connect_L', c_xyz=s_xyzL, c_connect=connectL,
               c_cmap='Spectral_r', c_linewidth=2., c_colorby='density',
               c_dynamic=(.1, 1.))

# Add right / front connectivity :
connectL = create_connect(s_xyzRF, 31., 31.5)
vb.add_connect('connect_L', c_xyz=s_xyzRF, c_connect=connectL,
               c_cmap='viridis', c_colorby='count', c_linewidth=1.5,
               c_dynamic=(.1, 1.))

# Add right / front connectivity :
connectL = create_connect(s_xyzRB, 31., 32.)
vb.add_connect('connect_L', c_xyz=s_xyzRB, c_connect=connectL,
               c_cmap='plasma', c_colorby='count', c_vmin=2.,
               c_under='gray', c_vmax=4., c_over='red',
               c_dynamic=(.5, 1.))


vb.show()
