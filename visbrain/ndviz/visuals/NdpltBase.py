"""
"""

from .NdpltMesh import NdpltMesh

__all__ = ['NdpltBase']


class NdpltBase(object):
    """My doc.
    """

    def __init__(self, data, sf, nd_axis=None, nd_color=None, nd_space=2,
                 nd_ax_name=None, nd_play=False, nd_force_col=None,
                 nd_rnd_dyn=(0.3, 0.9), nd_demean=True, nd_cmap='viridis',
                 nd_clim=None, nd_vmin=None, nd_under='gray', nd_vmax=None,
                 nd_over='red', nd_laps=1, nd_unicolor='gray', **kwargs):
        self.mesh = NdpltMesh(data, sf, axis=nd_axis, color=nd_color,
                              space=nd_space, ax_name=nd_ax_name, play=nd_play,
                              force_col=nd_force_col, rnd_dyn=nd_rnd_dyn,
                              demean=nd_demean, cmap=nd_cmap, clim=nd_clim,
                              vmin=nd_vmin, under=nd_under, vmax=nd_vmax,
                              over=nd_over, laps=nd_laps, unicolor=nd_unicolor)