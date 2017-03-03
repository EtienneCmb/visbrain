"""This example show how to display and control simple 1d signal."""

import numpy as np
from visbrain import Sleep
from scipy.io import loadmat

# mat = loadmat('sub-02_mat.mat')
# print(mat.keys())

nelec = 60
npts = 10000

data = np.random.rand(nelec, npts)
sf = 1024.
channel = ['channel_'+str(k) for k in range(nelec)]
hypno = np.random.rand(npts)

Sleep(data=data, channels=channel, sf=sf, hypno=hypno, downsample=100.).show()
