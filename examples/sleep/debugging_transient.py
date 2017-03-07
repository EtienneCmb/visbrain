import numpy as np
from visbrain.utils import transient

x = np.array([0, 0, 0, 1, 1, 1, 0, 0, 2, 2, 2, 3, 3, 2])
xvec = np.arange(len(x)) / 1024.

tr = transient(x, xvec)

print(tr)

# [ 0  2  5  7 10 12 13]