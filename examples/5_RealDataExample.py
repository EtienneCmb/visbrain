"""This example demonstrate how to display deep sources using MNI
coordinates
"""
from visbrain import vbrain
import numpy as np

data = np.load('RealDataExample.npz')

s_data = data['beta']
s_xyz = data['xyz']

vb = vbrain(s_xyz=s_xyz, s_data=s_data, cmap_vmin=-1, cmap_vmax=1, cmap='jet')
vb.show()