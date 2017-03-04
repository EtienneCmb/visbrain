"""This example show how to display and control simple 1d signal."""

import numpy as np
from visbrain import Sleep
from scipy.io import loadmat

#############################################################################
# REAL DATA EXAMPLE :
mat = loadmat('testing_database.mat')

data = mat['x']
hypnot = mat['hypno'].ravel()
channels = [str(k[0]) for k in mat['labels'][0][0:-2]]
print(data.shape, len(channels))

hypno = []
for k in hypnot:
	hypno += [k] * 100
hypno = np.array(hypno)
#############################################################################
# DEBUGGING EXAMPLE :
# nelec = 20
# npts = 1000000

# data = np.random.rand(nelec, npts)
# channels = ['channel_'+str(k) for k in range(nelec)]
# hypno = np.random.rand(npts)
sf = 512.

Sleep(data=data, channels=channels, sf=sf, hypno=hypno, downsample=100.).show()
