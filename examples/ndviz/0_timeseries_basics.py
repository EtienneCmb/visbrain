from visbrain import Ndviz
import numpy as np

y = np.random.rand(1000, 50, 20)

# y = np.random.normal(size=(1000, 10, 5)).astype(np.float32) + 100.
# y *= 200./y.max()

# y = np.arange(10).reshape(10, 1) + np.arange(10) + 11.5
# y = np.ascontiguousarray(y.astype(np.float32))


# y = np.sin(np.arange(1000)*2*np.pi*200/1024)[..., np.newaxis, np.newaxis]
# y = np.tile(y, (1, 30, 20)).astype(np.float32)
# y += np.random.rand(*y.shape)


# radius = 200
# r2 = np.arange(-radius, radius+1)**2
# r3 = r2.reshape(2*radius+1, 1) + r2
# r4 = 2 * np.pi * 1000 * np.abs(r3 - r3.max()) / (r3.max() * 1024.)
# y = np.sin(r4).astype(np.float32)
# # y = np.tile(y, (1, 1, 10))
# y += np.random.rand(*y.shape) / 10


# 0/0


# y = np.array([1, 1, 1, 1, 3, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 5, 5, 6, 7])
sf = 1024.


vbn = Ndviz(y, sf, nd_color='random', nd_laps=10, nd_cmap='inferno', nd_axis=None, lw=2)
vbn.show()


0, 1, 2