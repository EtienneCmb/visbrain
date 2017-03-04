"""This example show how to display and control simple 1d signal."""

import numpy as np
from timeit import timeit
from scipy.signal import spectrogram
from vispy.scene.visuals import Spectrogram
import matplotlib.pyplot as plt

nfft = 256
step = 128
sf = 1024
n = 1000

number = 1

t = np.arange(n) / sf
x = np.sin(2*np.pi*200*t) + np.random.rand(n)

# Vispy :

def f1():
    Spectrogram(x, fs=sf, n_fft=nfft, step=step)
t1 = timeit(f1, number=number)

mesh = Spectrogram(x, fs=sf, n_fft=nfft, step=step)
data_sp1 = mesh._data

# Scipy :
def f2():
    spectrogram(x, fs=sf, nperseg=nfft, noverlap=step) 
t2 = timeit(f1, number=number)

f, t, data_sp2 = spectrogram(x, fs=sf, nperseg=nfft, noverlap=step, window='hann') 

print('TIME 1: ', t1, '\nTIME 2: ', t2)
print(data_sp1.shape, data_sp2.shape)


plt.figure(0)
plt.subplot(1, 2, 1)
plt.pcolormesh(t, f, data_sp1)

plt.subplot(1, 2, 2)
plt.pcolormesh(t, f, 20 * np.log10(data_sp2))
plt.show()