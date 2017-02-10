from visbrain import Ndviz
import numpy as np

# y = np.random.rand(1000, 10, 20)

# y = np.random.normal(size=(1000, 10, 20))

# y = np.sin(np.arange(1000)) + np.random.rand(1000)

y = np.array([1, 1, 1, 1, 3, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 5, 5, 6, 7])
sf = 1024


vbn = Ndviz(y, sf, nd_color='dyn_minmax', nd_laps=10, nd_cmap='inferno', lw=1., nd_axis=None)
vbn.show()


