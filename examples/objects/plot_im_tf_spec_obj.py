"""
Image, time-frequency map and spectrogram objects
=================================================

Use and control image, time-frequency maps and spectrogram.

    * Display and configure an image (color, interpolation)
    * Compute and display time-frequency properties of a signal (spectrogram,
      wavelet based time-frequency maps or multi-taper)
"""
import numpy as np
from visbrain.objects import (ImageObj, TimeFrequencyObj, ColorbarObj,
                              SceneObj)

###############################################################################
# Scene creation
###############################################################################
# First, we define the scene and a few colorbar properties (like font size,
# colorbar width...)

CBAR_STATE = dict(cbtxtsz=12, txtsz=10., width=.1, rect=(-0.2, -2., 1., 4.),
                  cbtxtsh=4.)
sc = SceneObj(size=(1000, 600))

###############################################################################
# Create sample data
###############################################################################
# Then we create some data for 1) images (a basic diagonale image) and 2) a
# sine signal with a main frequency at 25hz

# Define a (10, 10) image
n = 10
image = np.r_[np.arange(n - 1), np.arange(n)[::-1]]
image = image.reshape(-1, 1) + image.reshape(1, -1)
image[np.diag_indices_from(image)] = 30.

# Define a 25hz sine
n, sf = 512, 256
time = np.arange(n) / sf  # time vector
data = np.sin(2 * np.pi * 25. * time) + np.random.rand(n)

###############################################################################
# Plot an image
###############################################################################
# Most basic plot of the image without further customization

im_basic = ImageObj('ex1', image)
sc.add_to_subplot(im_basic, row=0, col=0, title='Basic image', zoom=.9)

###############################################################################
# Interpolated image
###############################################################################
# The image can also be interpolated. Checkout the complete list on the
# VisPy website (vispy.visuals.ImageVisual)

im_interp = ImageObj('ex2', image, interpolation='bicubic')
sc.add_to_subplot(im_interp, row=0, col=1, title='Interpolated image', zoom=.9)

###############################################################################
# Color properties
###############################################################################
# The ImageObj allow several custom color properties (such as color
# thresholding, colormap control...)

# Create the image object
im_color = ImageObj('ex3', image, interpolation='bilinear', cmap='Spectral_r',
                    vmin=5., vmax=20., under='gray', over='darkred')
sc.add_to_subplot(im_color, row=0, col=2, title='Custom colors', zoom=.9)
# Get the colorbar of the image
cb_im_color = ColorbarObj(im_color, cblabel='Image data', **CBAR_STATE)
sc.add_to_subplot(cb_im_color, row=0, col=3, width_max=150, zoom=.9)

###############################################################################
# Spectrogram
###############################################################################
# Extract time-frequency properties using the Fourier transform

spec = TimeFrequencyObj('spec', data, sf, method='fourier', cmap='RdBu_r')
sc.add_to_subplot(spec, row=1, col=0, title='Spectrogram', zoom=.9)

###############################################################################
# Time-frequency map
###############################################################################
# Extract time-frequency properties using the wavelet convolution

tf = TimeFrequencyObj('tf', data, sf, method='wavelet')
sc.add_to_subplot(tf, row=1, col=1, title='Time-frequency map', zoom=.9)

###############################################################################
# Multi-taper
###############################################################################
# Extract time-frequency properties using multi-taper (need installation of
# lspopt package)

tf_mt = TimeFrequencyObj('mt', data, sf, method='multitaper', overlap=.7,
                         interpolation='bicubic', cmap='Spectral_r')
sc.add_to_subplot(tf_mt, row=1, col=2, title='Multi-taper', zoom=.9)
cb_tf_win = ColorbarObj(tf_mt, cblabel='Power', **CBAR_STATE)
sc.add_to_subplot(cb_tf_win, row=1, col=3, width_max=150, zoom=.9)

# Display the scene
sc.preview()
