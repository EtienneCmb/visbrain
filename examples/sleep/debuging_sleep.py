"""This example show how to display and control simple 1d signal."""

import numpy as np
from visbrain import Sleep
from scipy.io import loadmat

torun = 'big'

###########################################################################
# LOAD BY GUI :
if torun == 'none':
    file = None
    hypno_file = None
    data = None
    hypno = None
    channels = None
    sf = None

###########################################################################
# LOAD BY DATASET :
elif torun == 'small':
    sf = 100.
    mat = loadmat('testing_database.mat')

    data = np.ascontiguousarray(mat['x'], dtype=np.float32)
    hypnot = mat['hypno'].ravel()
    channels = [str(k[0]) for k in mat['labels'][0][0:-2]]

    hypno = []
    for k in hypnot:
        hypno += [k] * 100
    hypno = np.ascontiguousarray(hypno, dtype=np.float32)

    file = None
    hypno_file = None

###########################################################################
# LOAD BY PATH :
elif torun == 'big':
    file = '/home/etienne/wetransfer-ff7857/s101_sleep.eeg'
    hypno_file = '/home/etienne/wetransfer-ff7857/s101_jbe.hyp'
    data = None
    channels = None
    sf = None
    hypno = None

###########################################################################
# DEBUGGING EXAMPLE :
elif torun == 'rnd':
    sf = 512.
    nelec = 3
    npts = 100000

    data = 10*np.random.rand(nelec, npts)
    channels = ['channel_'+str(k) for k in range(nelec)]
    hypno = np.random.rand(npts)

    file = None
    hypno_file = None


sp = Sleep(file=file, hypno_file=hypno_file, data=data, channels=channels,
           sf=sf, downsample=100., hypno=hypno, line='gl', axis=False)
sp._fcn_applyDetection()
sp.show()
# s = Sleep()
# s.show()


