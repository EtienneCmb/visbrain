"""
Plot a 3D array of data
=======================

Plot and inspect a 3D array of data.

This example is an extension to the previous one (01_2d_signals.py). This time,
instead of automatically re-organizing the 2D grid, the program use the number
of channels for the number of rows in the grid and the number of trials for the
number of columns.
To illustrate this point, we generate a random EEG dataset composed with 20
channels, 10 trials of 4000 points each. The 2D grid will have a shape of
(20 rows, 10 columns).

.. image:: ../../_static/examples/ex_3d_signal.png
"""
from itertools import product
from visbrain.gui import Signal
from visbrain.utils import generate_eeg

sf = 512.  # sampling frequency
n_pts = 4000  # number of time points
n_channels = 20  # number of EEG channels
n_trials = 10  # number of trials in the dataset

"""Generate a random EEG dataset of shape (n_channels, n_trials, n_pts).
Also get the associated time vector with the same length as the data.
"""
data, time = generate_eeg(sf=sf, n_pts=n_pts, n_trials=n_trials,
                          n_channels=n_channels, smooth=200, noise=1000)
time += 8.  # force the time vector to start at 8 seconds
time *= 1000.  # millisecond conversion

"""The data have a shape of (20, 10, 4000). Hence, the time dimension is
defined as the last axis i.e `axis=2`
"""
axis = 2  # localization of the time axis

"""Add a label to the x-axis (xlabel), y-axis (ylabel) and a title
"""
xlabel = 'Time (ms)'
ylabel = 'Amplitude (uV)'
title = 'Plot of a 1-d signal'

"""Build the title to add to each time-series in the grid
"""
st = 'Channel {} - trial {}'
it = product(range(n_channels), range(n_trials))
gtitles = [st.format(c, t) for c, t in it]  # grid titles
gfz = 7.  # grid titles font-size
gc = 'gray'  # grid color

Signal(data, sf=sf, axis=axis, time=time, xlabel=xlabel, ylabel=ylabel,
       title=title, grid_titles=gtitles, grid_font_size=gfz,
       grid_color=gc).show()
