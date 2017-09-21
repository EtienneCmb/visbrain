"""Group functions for automatic scoring of sleep."""

import numpy as np
from scipy.signal import hilbert, savgol_filter
from scipy.stats import zscore
from ..filtering import filt, morlet

__all__ = ['']


def autoscoring(elec, sf):
    """
    """

    # freqs = np.array([0.5, 4, 8, 12, 16])
    # # delta, theta, alpha, beta = _wavelet_bpower(data, freqs, sf, norm=True)
    #
    # # Downsample
    # delta = delta[::sf]
    # theta = theta[::sf]
    # alpha = alpha[::sf]
    # beta = beta[::sf]
    #
    # # Filter
    # delta = savgol_filter(delta, 59, 2)
    # theta = savgol_filter(theta, 59, 2)
    # alpha = savgol_filter(alpha, 59, 2)
    # beta = savgol_filter(beta, 59, 2)
    #
    # # Ranking
    # zdelta = zscore(delta)
    # ztheta = zscore(theta)
    # zalpha = zscore(alpha)
    # zbeta = zscore(beta)
    #
    # max_sbp = np.maximum.reduce([zdelta, ztheta, zalpha, zbeta])
    #
    # predominant = np.zeros(shape=delta.shape, dtype=int)
    #
    # # Find N3 period
    # for i, j in enumerate(max_sbp):
    #     predominant[i] = 3 if j == zdelta[i] else 0

    pass
