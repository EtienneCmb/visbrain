"""
Add time series
===============

This example demonstrate how to display time-series attached to sources. The
time-series can then be controlled from the GUI in the Sources/Time-series tab.

Download source's coordinates (xyz_sample.npz) :
https://www.dropbox.com/s/whogfxutyxoir1t/xyz_sample.npz?dl=1

.. image:: ../../_static/examples/ex_time_series.png
"""
import numpy as np

from visbrain.gui import Brain
from visbrain.objects import TimeSeries3DObj, SourceObj
from visbrain.io import download_file

# Load the xyz coordinates and corresponding subject name :

s_xyz = np.load(download_file('xyz_sample.npz', astype='example_data'))['xyz']
s_xyz = s_xyz[4::25, ...]
s_text = [str(k) for k in range(s_xyz.shape[0])]
s_textsize = 1.5

"""Define a source object
"""
s_obj = SourceObj('MySources', s_xyz, symbol='disc', color='green')

"""Define the time-series data
"""
sf = 512.                   # Sampling frequency
n_time_points = 700         # Number of time points
n_sources = s_xyz.shape[0]  # Number of sources
time = np.mgrid[0:n_sources, 0:n_time_points][1] / sf  # Time vector
# Randomize the amplitude and the phase of sine :
amp = np.random.randint(2, 20, n_sources).reshape(-1, 1)
pha = np.random.randint(1, 7, n_sources).reshape(-1, 1)
# Build the time series of shape (n_sources, n_time_points) :
ts_data = amp * np.sin(2 * np.pi * pha * time)
ts_data += np.random.randn(n_sources, n_time_points)

# Use a boolean vector to hide/display time-series :
ts_to_mask = [5, 7, 11, 3, 14, 17, 22, 23]
ts_select = np.ones((s_xyz.shape[0],), dtype=bool)
ts_select[ts_to_mask] = False

# Time-series (TS) graphical properties :
ts_amp = 5.4            # TS graphical amplitude
ts_width = 15.7         # TS graphical width
ts_color = 'orange'     # TS color
ts_dxyz = (1., 2., 5.)  # TS offset along the (x, y, z) axes
ts_lw = 2.2             # TS line-width

"""Define the 3-D time-series object
"""
ts = TimeSeries3DObj('Ts1', ts_data, s_xyz, select=ts_select, ts_amp=ts_amp,
                     ts_width=ts_width, line_width=ts_lw, translate=ts_dxyz,
                     color=ts_color)

vb = Brain(time_series_obj=ts, source_obj=s_obj)
vb.show()
