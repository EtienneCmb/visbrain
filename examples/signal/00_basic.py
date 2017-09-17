import numpy as np
from visbrain import Signal

kwargs = {'xlabel': 'xlabel', 'ylabel': 'ylabel', 'title': 'title',
          'display_grid': True, 'color': 'darkgray', 'symbol': 'x',
          'title_font_size': 20, 'axis_font_size': 18, 'tick_font_size': 8,
          'axis_color': 'blue', 'bgcolor': 'white', 'enable_grid': True,
          'display_signal': False}

data = 100 * np.random.rand(7, 4000) + 10.
# data = np.sin(2 * np.pi * 4 * np.arange(10000) / 1024) + 100
Signal(data, axis=-1, sf = 1024., **kwargs).show()