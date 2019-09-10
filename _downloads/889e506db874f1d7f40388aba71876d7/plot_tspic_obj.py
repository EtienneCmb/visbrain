"""
Time-series and pictures 3D (TimeSeries3DObj & Picture3DObj): complete tutorial
===============================================================================

Illustration of the main features of 3d time-series and pictures. This
include :

    * Define and plot of spatially distributed time-series (TS) and pictures
    * Masking TS and pictures
    * Custom properties (i.e line width, colors, size...)
"""
import numpy as np

from scipy.signal import spectrogram

from visbrain.objects import TimeSeries3DObj, Picture3DObj, SceneObj
from visbrain.utils import generate_eeg


###############################################################################
# Define sample data and scene
###############################################################################
# 3D time-series and pictures need to be attached to sources define in a 3D
# space.

# Define 5 sources
xyz = np.array([[0, .5, 0], [1, -4, 3], [10, 2, 8], [1, 7, 12], [-4, 5, 6]])
n_sources = xyz.shape[0]
# Define the time-series of those 5 sources
ts_data = generate_eeg(sf=512., n_channels=n_sources, noise=5., smooth=5)[0]
# Compute the spectrogram of the 5 time-series
pic_data = []
for k in range(n_sources):
    pic_data += [spectrogram(ts_data[k, :], 512., nperseg=128, noverlap=10)[2]]
pic_data = np.asarray(pic_data)
clim = (.01 * pic_data.min(), .01 * pic_data.max())

# Scene definition
sc = SceneObj()

###############################################################################
# Basic plot
###############################################################################
# Basic plot without further customizations

# Define time-series and picture objects
ts_0 = TimeSeries3DObj('t0', ts_data, xyz, antialias=True)
pic_0 = Picture3DObj('p0', pic_data, xyz, clim=clim)
# Add those objects to the scene
sc.add_to_subplot(ts_0, row=0, col=0, zoom=.2, title='Basic 3D TS plot')
sc.add_to_subplot(pic_0, row=0, col=1, zoom=.5, title='Basic 3D pictures plot')

###############################################################################
# Subset selection
###############################################################################
# Select a subset of time-series and pictures using either a list of intergers
# or booleans

# Define a select variables using either intergers or boolean values
s_ts = [0, 2, 4]
s_pic = [True, False, True, False, True]
# Define time-series and picture objects
ts_1 = TimeSeries3DObj('t1', ts_data, xyz, antialias=True, select=s_ts)
pic_1 = Picture3DObj('p1', pic_data, xyz, clim=clim, select=s_pic, cmap='bwr')
# Add those objects to the scene
sc.add_to_subplot(ts_1, row=1, col=0, zoom=.2, title='Select a TS subset')
sc.add_to_subplot(pic_1, row=1, col=1, zoom=.5,
                  title='Select a subject of pictures')

###############################################################################
# Shape and color properties
###############################################################################
# Customize colors, time-series amplitude and width, pictures height and width

# Define time-series and picture objects
ts_2 = TimeSeries3DObj('t2', ts_data, xyz, antialias=True, color='slateblue',
                       line_width=2., ts_amp=4, ts_width=10)
pic_2 = Picture3DObj('p2', pic_data, xyz, clim=clim, cmap='Spectral_r',
                     pic_width=10, pic_height=15)
# Add those objects to the scene
sc.add_to_subplot(ts_2, row=2, col=0, zoom=.2,
                  title='Custom TS color and shape')
sc.add_to_subplot(pic_2, row=2, col=1, zoom=.5,
                  title='Custom picture color and shape')

# Finally, display the scene
sc.preview()
