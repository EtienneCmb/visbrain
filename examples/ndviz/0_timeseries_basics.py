from visbrain import Ndviz
import numpy as np

# y = np.random.rand(1000, 10, 20)

y = np.random.normal(size=(1000, 103)).astype(np.float32) + 100.
# y *= 200./y.max()

print(y.dtype)
# y /= y.max()

# y = np.sin(np.arange(1000)*2*np.pi*200/1024) + np.random.rand(1000)

# y = np.array([1, 1, 1, 1, 3, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 5, 5, 6, 7])
sf = 1024.


vbn = Ndviz(y, sf, nd_color='random', nd_laps=10, nd_cmap='inferno', nd_axis=None, lw=0.1)
vbn.show()


