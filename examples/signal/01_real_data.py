import numpy as np
from brainpipe.sys.tools import loadfile

from visbrain import Signal

kwargs = {'xlabel': 'Time (second)', 'ylabel': 'Amplitude (uV)', 'title': 'Time-series of a premotor site',
          'display_grid': False, 'color': 'white', 'symbol': 'x',
          'axis_color': 'white', 'bgcolor': (.1, .1, .1),
          'line_rendering': 'agg', 'enable_grid': True}

raw = loadfile('/media/etienne/E438C4AE38C480D2/Users/Etienne Combrisson/Mes documents/MATLAB/Sujets/C_rev/Données/bipolarised_C_rev_mouse_RH_1.mat')['datab']

Signal(raw.astype(np.float32).mean(-1), sf=1024, axis=1, **kwargs).show()