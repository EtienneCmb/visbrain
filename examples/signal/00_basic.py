import numpy as np
from visbrain import Signal

kwargs = {'xlabel': 'xlabel', 'ylabel': 'ylabel', 'title': 'title',
          'display_grid': False, 'color': 'darkgray', 'symbol': 'x',
          'title_font_size': 20, 'axis_font_size': 18, 'tick_font_size': 8,
          'axis_color': 'blue', 'bgcolor': 'white', 'enable_grid': True,
          'display_signal': True, 'annotations': '/home/etienne/annotations.txt'}

case = 4

if case == 0:  # 1-D
    data = 100. * np.random.randn(4000) + 100.
    axis = 0
elif case == 1:  # 2-D axis=0
    data = 100. * np.random.randn(4000, 400) + 100.
    data[:, 4] = np.arange(4000)
    axis = 0
elif case == 2:  # 2-D axis=1
    data = 100. * np.random.randn(6, 4000) + 100.
    data[2, :] = np.arange(4000)
    axis = 1
elif case == 3:  # 3-D axis=0
    data = 100 * np.random.randn(100, 7, 4000) + 100.
    data[13, 5, :] = np.arange(4000)
    axis = -1
elif case == 4:  # 3-D axis=1, large
    data = 100 * np.random.randn(7, 10000, 20) + 100.
    data[5, :, 13] = np.arange(10000) + 2
    axis = 1
elif case == 5:  # 3-D axis=1, small
    data = 100 * np.random.randn(20, 4000, 7) + 100.
    data[13, :, 5] = np.arange(4000)
elif case == 6:  # 3-D axis=2
    axis = 1



# sf = 1024.
# npts = 200
# time = np.arange(-npts/2, npts/2)/1024.
# # Create a 2d signal :
# data = np.sinc(2*10*time).astype(np.float32)
# data = data.reshape(len(data), 1) + data
# # Add a little bit of noise :
# data = data**2 + np.random.rand(*data.shape) / 10

Signal(data, axis=axis, sf=1024., **kwargs).show()