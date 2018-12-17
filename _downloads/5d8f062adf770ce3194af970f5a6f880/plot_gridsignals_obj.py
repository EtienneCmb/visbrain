"""
Grid of signals object (GridSignalsObj) : complete tutorial
===========================================================

This example illustrate the main functionalities and inputs of the grid of
time-series object i.e :

  * Display 1D, 2D or 3D array
  * Compatibility with MNE-Python objects (mne.io.Raw, mne.io.RawArray,
    mne.Epochs)
  * Display your data either as a grid, a single row or a single column

Note that this example uses MNE-Python, hence, it need to be installed to be
fully functional.
"""
import numpy as np
from itertools import product

import mne

from visbrain.objects import GridSignalsObj, SceneObj
from visbrain.utils import generate_eeg


###############################################################################
# Scene creation
###############################################################################
# The SceneObj is Matplotlib subplot like in which, you can add visbrain's
# objects. We first create the scene with a black background, a fixed size

# Scene creation
sc = SceneObj(bgcolor='black', size=(1400, 1000))

###############################################################################
# Generate random data
###############################################################################
# Here we generate a random 3D dataset with 5 channels and 4 trials per channel
# Note that here we geneate a 3D dataset but you can also pass a 1D or 2D
# dataset

sf = 512.       # sampling frequency
n_pts = 1000    # number of time points
n_channels = 5  # number of channels
n_trials = 4    # number of trials
data_3d = generate_eeg(n_pts=n_pts, n_channels=n_channels, n_trials=n_trials,
                       f_max=20., smooth=200, noise=1000)[0]
channels = ['Channel %i' % (k + 1) for k in range(n_channels)]
trials = ['Trial %i' % k for k in range(n_trials)]

# Generate the titles of each signal
title = ['%s - %s' % (k, i) for k, i in product(channels, trials)]

# Plot the data as a grid and add it to the scene
g_obj_grid = GridSignalsObj('3d', data_3d, title=title, plt_as='grid')
sc.add_to_subplot(g_obj_grid, title='Grid of 3D data')


###############################################################################
# Plot MNE-Python data
###############################################################################
# The GridSignalsObj is also compatible with several MNE-Python instance (i.e
# mne.io.Raw, mne.io.RawArray and mne.Epochs). Here we illustrate how to plot
# epochs in a grid.

# Create MNE data
data_mne = generate_eeg(n_pts=n_pts, n_channels=n_channels, f_max=20.,
                        smooth=200, noise=1000)[0]
# Create info required for the definition of the RawArray
info = mne.create_info(channels, sf)
# Create a RawArray MNE instance
mne_raw = mne.io.RawArray(data_mne, info)
# Specify where each event start and finish
start = np.linspace(0, 800, 5).astype(int)
end = np.linspace(100, 900, 5).astype(int)
events = np.c_[start, end, np.arange(len(start))]
# Create a MNE Epochs instance
epochs = mne.Epochs(mne_raw, events)

g_obj_mne = GridSignalsObj('3d', epochs, plt_as='grid', color='green')
sc.add_to_subplot(g_obj_mne, col=1, title='Plot MNE epochs as a grid')


###############################################################################
# Configure your plotting type
###############################################################################
# By default, the data is plotted as a grid of signals. But this behavior can
# be modified using the `plt_as` parameter. You can use `plt_as='row'` or
# `plt_as='col'` to display your signals respectively in a unique row or column
# When you plot your data as a row or as a column, you can specify the number
# of time-series using the `n_signals` inut parameter

plt_as = 'col'  # {'grid', 'row', 'col'}
g_obj_col = GridSignalsObj('3d', data_3d, title=title, plt_as='col', lw=4.,
                           title_bold=False, color='orange', n_signals=3)

sc.add_to_subplot(g_obj_col, col=2, title='Plot data in a single col')

sc.preview()
