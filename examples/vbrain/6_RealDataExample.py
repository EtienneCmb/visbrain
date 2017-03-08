"""This example demonstrate how to display deep sources using MNI coordinates.
"""
from visbrain import vbrain
import numpy as np

data = np.load('RealDataExample.npz')

s_data = data['beta']
s_xyz = data['xyz']

vb = vbrain(s_xyz=s_xyz, s_data=s_data, s_cmap_vmin=-1, s_cmap_vmax=1,
            s_cmap='jet', s_cmap_clim=(-1, 1))
vb.show()
