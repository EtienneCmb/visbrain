"""This example show how to display and control simple 1d signal."""

import numpy as np
from visbrain import Sleep
from scipy.io import loadmat

sf = 100.
#############################################################################
# REAL DATA EXAMPLE :
mat = loadmat('testing_database.mat')

data = mat['x']
hypnot = mat['hypno'].ravel()
channels = [str(k[0]) for k in mat['labels'][0][0:-2]]

hypno = []
for k in hypnot:
    hypno += [k] * 100
hypno = np.array(hypno)
#############################################################################
# DEBUGGING EXAMPLE :
# sf = 512.
# nelec = 20
# npts = 14745600
# nelec = 3
# npts = 1000000

# data = 10*np.random.rand(nelec, npts)
# channels = ['channel_'+str(k) for k in range(nelec)]
# hypno = np.random.rand(npts)


Sleep(data=data, channels=channels, sf=sf, downsample=100., hypno=hypno,
      line='gl', axis=False).show()
# s = Sleep()
# s.show()


