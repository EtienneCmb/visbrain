import numpy as np
from visbrain import GridSignals

kwargs = {'xlabel': 'xlabel', 'ylabel': 'ylabel', 'title': 'title',
          'display_grid': False, 'color': 'darkgray', 'symbol': 'x',
          'title_font_size': 20, 'axis_font_size': 18, 'tick_font_size': 8,
          'axis_color': 'blue'}

data = np.exp(np.random.rand(10000, 10, 5) + 10.)
GridSignals(data, axis=0, **kwargs).show()