"""
Interface customization
=======================

Use custom color, font size...

.. image:: ../../_static/examples/ex_custom_interface.png
"""
from visbrain.gui import Signal
from visbrain.utils import generate_eeg

sf = 512.  # sampling frequency
n_pts = 4000  # number of time points
n_trials = 125  # number of trials in the dataset

"""Generate a random EEG vector of shape (n_trials, n_pts). This time, we
smooth signals and decrease the noise on it.
"""
data, _ = generate_eeg(sf=sf, n_pts=n_pts, n_trials=n_trials, smooth=200,
                       noise=1000)

gtitles = ['Trial ' + str(k) for k in range(n_trials)]  # grid titles
gfz = 8.  # grid titles font-size

"""Define a dictionary with interface customization entries
"""
kwargs = {'xlabel': 'xlabel', 'ylabel': 'ylabel', 'title': 'title',
          'color': 'lightgray', 'marker_symbol': 'x', 'title_font_size': 20,
          'hist_nbins': 100, 'line_lw': 2.5, 'tf_norm': 3,
          'tf_interp': 'nearest', 'tf_cmap': 'Spectral_r',
          'tf_baseline': (250, 750), 'tf_av_window': 100, 'tf_av_overlap': .5,
          'tf_clim': (-.5, .5), 'axis_font_size': 18, 'tick_font_size': 8,
          'axis_color': 'white', 'bgcolor': (.1, .1, .1), 'form': 'marker',
          'grid_titles': gtitles, 'grid_font_size': gfz,
          'grid_titles_color': 'white'}

sg = Signal(data, sf=sf, axis=-1, **kwargs)
sg.show()
