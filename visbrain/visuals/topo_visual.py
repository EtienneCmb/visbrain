"""Topoplot visual.

Parents description :

node -> rescale x800 (solve GL issues for small plots)
    node_headfull -> scale (-1, 1)
        node_head -> recenter + (T4, Fpz)
        node_chan -> translate (0, 0, 10.) (objects superposition)

Authors: Etienne Combrisson <e.combrisson@gmail.com>

License: BSD (3-clause)
"""
import logging

import numpy as np
from scipy.interpolate import interp2d

from vispy import scene
from vispy.scene import visuals
import vispy.visuals.transforms as vist

from ..utils import (array2colormap, color2vb, mpl_cmap, normalize,
                     vpnormalize, vprecenter)
from ..io import download_file
from .cbar import CbarVisual

logger = logging.getLogger('visbrain')

__all__ = ('TopoMesh')


class TopoMesh(object):
    """Create a TopoMesh VisPy object.

    Parameters
    ----------
    xyz : array_like | None
        Array of source's coordinates.
    channels : list | None
        List of channel names.
    system : {'cartesian', 'spherical'}
        Coordinate system.
    unit : {'degree', 'rad'}
        If system is 'spherical', specify if angles are in degrees or radians.
    title : string | None
        Title of the topoplot.
    title_color : array_like/string | 'black'
        Color for the title.
    title_size : float | 20.
        Size of the title.
    line_color : array_like/string | 'black'
        Color of lines for the head, nose and eras.
    line_width : float | 4.
        Line width for the head, nose and eras.
    chan_size : float | 12.
        Size of channel names text.
    chan_mark_color : array_like/string | 'white'
        Color of channel markers.
    chan_mark_symbol : string | 'disc'
        Symbol to use for markers. Use disc, arrow, ring, clobber, square,
        diamond, vbar, hbar, cross, tailed_arrow, x, triangle_up,
        triangle_down, and star.
    chan_txt_color : array_like/string | 'black'
        Color of channel names.
    bgcolor : array_like/string | 'white'
        Background color.
    cbar : bool | True
        Attach a colorbar to the topoplot.
    cb_txt_size : float | 16.
        Text size for the colorbar limits and label.
    margin : float | .05
        Margin percentage.
    parent : VisPy.parent | None
        VisPy parent.
    """

    def __init__(self, xyz=None, channels=None, system='cartesian',
                 unit='degree', title=None, title_color='black',
                 title_size=20., line_color='black', line_width=4.,
                 chan_size=12., chan_offset=(0., 0., 0.),
                 chan_mark_color='white', chan_mark_symbol='disc',
                 chan_txt_color='black', bgcolor='white', cbar=True,
                 cb_txt_size=10., margin=.05, parent=None):
        """Init."""
        # ======================== VARIABLES ========================
        self._bgcolor = color2vb(bgcolor)
        scale = 800.  # fix GL bugs for small plots
        pos = np.zeros((1, 3), dtype=np.float32)
        # Colors :
        title_color = color2vb(title_color)
        line_color = color2vb(line_color)
        chan_txt_color = color2vb(chan_txt_color)
        self._chan_mark_color = color2vb(chan_mark_color)
        self._chan_mark_symbol = chan_mark_symbol
        # Disc interpolation :
        self._interp = .1
        self._pix = 64
        csize = int(self._pix / self._interp) if self._interp else self._pix
        l = csize / 2  # noqa

        # ======================== NODES ========================
        # Main topoplot node :
        self.node = scene.Node(name='Topoplot', parent=parent)
        self.node.transform = vist.STTransform(scale=[scale] * 3)
        # Headset + channels :
        self.node_headfull = scene.Node(name='HeadChan', parent=self.node)
        # Headset node :
        self.node_head = scene.Node(name='Headset', parent=self.node_headfull)
        # Channel node :
        self.node_chan = scene.Node(name='Channels', parent=self.node_headfull)
        self.node_chan.transform = vist.STTransform(translate=(0., 0., -10.))
        # Cbar node :
        self.node_cbar = scene.Node(name='Channels', parent=self.node)
        # Dictionaries :
        kw_line = {'width': line_width, 'color': line_color,
                   'parent': self.node_head}

        # ======================== PARENT VISUALS ========================
        # Main disc :
        self.disc = visuals.Image(pos=pos, name='Disc', parent=self.node_head,
                                  interpolation='bilinear')
        # Title :
        self.title = visuals.Text(text=title, pos=(0., .6, 0.), name='Title',
                                  parent=self.node, font_size=title_size,
                                  color=title_color, bold=True)
        self.title.font_size *= 1.1

        # ======================== HEAD / NOSE / EAR ========================
        # ------------------ HEAD ------------------
        # Head visual :
        self.head = visuals.Line(pos=pos, name='Head', **kw_line)
        # Head circle :
        theta = np.arange(0, 2 * np.pi, 0.001)
        head = np.full((len(theta), 3), -1., dtype=np.float32)
        head[:, 0] = l * (1. + np.cos(theta))
        head[:, 1] = l * (1. + np.sin(theta))
        self.head.set_data(pos=head)

        # ------------------ NOSE ------------------
        # Nose visual :
        self.nose = visuals.Line(pos=pos, name='Nose', **kw_line)
        # Nose data :
        wn, hn = csize * 50. / 512., csize * 30. / 512.
        nose = np.array([[l - wn, 2 * l - wn, 2.],
                         [l, 2 * l + hn, 2.],
                         [l, 2 * l + hn, 2.],
                         [l + wn, 2 * l - wn, 2.]
                         ])
        self.nose.set_data(pos=nose, connect='segments')

        # ------------------ EAR ------------------
        we, he = csize * 10. / 512., csize * 30. / 512.
        ye = l + he * np.sin(theta)
        # Ear left data :
        self.earL = visuals.Line(pos=pos, name='EarLeft', **kw_line)
        # Ear left visual :
        ear_l = np.full((len(theta), 3), 3., dtype=np.float32)
        ear_l[:, 0] = 2 * l + we * np.cos(theta)
        ear_l[:, 1] = ye
        self.earL.set_data(pos=ear_l)

        # Ear right visual :
        self.earR = visuals.Line(pos=pos, name='EarRight', **kw_line)
        # Ear right data :
        ear_r = np.full((len(theta), 3), 3., dtype=np.float32)
        ear_r[:, 0] = 0. + we * np.cos(theta)
        ear_r[:, 1] = ye
        self.earR.set_data(pos=ear_r)

        # ================== CHANNELS ==================
        # Channel's markers :
        self.chanMarkers = visuals.Markers(pos=pos, name='ChanMarkers',
                                           parent=self.node_chan)
        # Channel's text :
        self.chanText = visuals.Text(pos=pos, name='ChanText',
                                     parent=self.node_chan, anchor_x='center',
                                     color=chan_txt_color,
                                     font_size=chan_size)

        # ================== CAMERA ==================
        self.rect = ((-scale / 2) * (1 + margin),
                     (-scale / 2) * (1 + margin),
                     scale * (1. + cbar * .3 + margin),
                     scale * (1.11 + margin))

        # ================== CBAR ==================
        if cbar:
            self.cbar = CbarVisual(cbtxtsz=1.2 * cb_txt_size,
                                   txtsz=cb_txt_size, txtcolor=title_color,
                                   cbtxtsh=2., parent=self.node_cbar)
            self.node_cbar.transform = vist.STTransform(scale=(.6, .4, 1.),
                                                        translate=(.6, 0., 0.))

        # ================== COORDINATES ==================
        auto = self._get_channel_coordinates(xyz, channels, system, unit)
        if auto:
            eucl = np.sqrt(self._xyz[:, 0]**2 + self._xyz[:, 1]**2).max()
            self.node_head.transform = vpnormalize(head, dist=2 * eucl)
            # Rescale between (-1:1, -1:1) = circle :
            circle = vist.STTransform(scale=(.5 / eucl, .5 / eucl, 1.))
            self.node_headfull.transform = circle
            # Text translation :
            tr = np.array([0., .8, 0.]) + np.array(chan_offset)
        else:
            # Get coordinates of references along the x and y-axis :
            ref_x, ref_y = self._get_ref_coordinates()
            # Recenter the topoplot :
            t = vist.ChainTransform()
            t.prepend(vprecenter(head))
            # Rescale (-ref_x:ref_x, -ref_y:ref_y) (ref_x != ref_y => ellipse)
            coef_x = 2 * ref_x / head[:, 0].max()
            coef_y = 2 * ref_y / head[:, 1].max()
            t.prepend(vist.STTransform(scale=(coef_x, coef_y, 1.)))
            self.node_head.transform = t
            # Rescale between (-1:1, -1:1) = circle :
            circle = vist.STTransform(scale=(.5 / ref_x, .5 / ref_y, 1.))
            self.node_headfull.transform = circle
            # Text translation :
            tr = np.array([0., .04, 0.]) + np.array(chan_offset)
        self.chanText.transform = vist.STTransform(translate=tr)

        # ================== GRID INTERPOLATION ==================
        # Interpolation vectors :
        x = y = np.arange(0, self._pix, 1)
        xnew = ynew = np.arange(0, self._pix, self._interp)

        # Grid interpolation function :
        def _grid_interpolation(grid):
            f = interp2d(x, y, grid, kind='linear')
            return f(xnew, ynew)
        self._grid_interpolation = _grid_interpolation

    def __len__(self):
        """Return the number of channels."""
        return self._nchan

    def __bool__(self):
        """Return if coordinates exist."""
        return hasattr(self, '_xyz')

    def set_data(self, data, levels=None, level_colors='white', cmap='viridis',
                 clim=None, vmin=None, under='gray', vmax=None, over='red',
                 cblabel=None):
        """Set data to the topoplot.

        Parameters
        ----------
        data : array_like
            Array of data of shape (n_channels)
        levels : array_like/int | None
            The levels at which the isocurve is constructed.
        level_colors : string/array_like | 'white'
            The color to use when drawing the line. If a list is given, it
            must be of shape (Nlev), if an array is given, it must be of
            shape (Nlev, ...). and provide one color per level
            (rgba, colorname). By default, all levels are whites.
        cmap : string | None
            Matplotlib colormap (like 'viridis', 'inferno'...).
        clim : tuple/list | None
            Colorbar limit. Every values under / over clim will
            clip.
        vmin : float | None
            Every values under vmin will have the color defined
            using the under parameter.
        vmax : float | None
            Every values over vmin will have the color defined
            using the over parameter.
        under : tuple/string | None
            Matplotlib color under vmin.
        over : tuple/string | None
            Matplotlib color over vmax.
        cblabel : string | None
            Colorbar label.
        """
        # ================== XYZ / CHANNELS / DATA ==================
        xyz = self._xyz[self._keeponly]
        channels = list(np.array(self._channels)[self._keeponly])
        data = np.asarray(data, dtype=float).ravel()
        if len(data) == len(self):
            data = data[self._keeponly]

        # =================== CHANNELS ===================
        # Markers :
        radius = normalize(data, 10., 30.)
        self.chanMarkers.set_data(pos=xyz, size=radius, edge_color='black',
                                  face_color=self._chan_mark_color,
                                  symbol=self._chan_mark_symbol)
        # Names :
        if channels is not None:
            self.chanText.text = channels
            self.chanText.pos = xyz

        # =================== GRID ===================
        pos_x, pos_y = xyz[:, 0], xyz[:, 1]
        xmin, xmax = pos_x.min(), pos_x.max()
        ymin, ymax = pos_y.min(), pos_y.max()
        xi = np.linspace(xmin, xmax, self._pix)
        yi = np.linspace(ymin, ymax, self._pix)
        xh, yi = np.meshgrid(xi, yi)
        grid = self._griddata(pos_x, pos_y, data, xh, yi)

        # =================== INTERPOLATION ===================
        if self._interp is not None:
            grid = self._grid_interpolation(grid)
        csize = max(self._pix, grid.shape[0])
        # Variables :
        l = csize / 2  # noqa
        y, x = np.ogrid[-l:l, -l:l]
        mask = x**2 + y**2 < l**2
        nmask = np.invert(mask)

        # =================== DISC ===================
        # Force min < off-disc values < max :
        grid[nmask] = data.mean()
        grid = normalize(grid, data.min(), data.max())
        clim = (data.min(), data.max()) if clim is None else clim
        image = array2colormap(grid, cmap=cmap, clim=clim, vmin=vmin,
                               vmax=vmax, under=under, over=over)
        image[nmask] = self._bgcolor
        self.disc.set_data(image)

        # =================== COLORBAR ===================
        if hasattr(self, 'cbar'):
            self.cbar.clim = clim
            self.cbar.cmap = cmap
            self.cbar.isvmin = vmin is not None
            self.cbar.vmin = vmin
            self.cbar.under = under
            self.cbar.isvmax = vmax is not None
            self.cbar.vmax = vmax
            self.cbar.over = over
            self.cbar.cblabel = cblabel

        # =================== LEVELS ===================
        if levels is not None:
            if isinstance(levels, int):
                levels = np.linspace(grid.min(), grid.max(), levels)
            if isinstance(level_colors, str):
                # Get colormaps :
                cmaps = mpl_cmap(bool(level_colors.find('_r') + 1))
                if level_colors in cmaps:
                    level_colors = array2colormap(levels, cmap=level_colors)
            grid[nmask] = np.inf
            self.iso = visuals.Isocurve(data=grid, parent=self.node_head,
                                        levels=levels, color_lev=level_colors,
                                        width=2.)
            self.iso.transform = vist.STTransform(translate=(0., 0., -5.))

    def _get_channel_coordinates(self, xyz, channels, system, unit):
        """Get channel coordinates.

        Parameters
        ----------
        xyz : array_like | None
            Array of source's coordinates.
        channels : list | None
            List of channel names.
        system : {'cartesian', 'spherical'}
            Coordinate system.
        unit : string | {'degree', 'rad'}
            If system is 'spherical', specify if angles are in degrees or
            radians.
        """
        # =====================
        if (xyz is None) and (channels is None):  # Both None
            raise ValueError("You must either define sources using the xyz or"
                             " channels inputs")
        elif isinstance(xyz, np.ndarray):  # xyz exist
            if xyz.shape[1] not in [2, 3]:
                raise ValueError("Shape of xyz must be (nchan, 2) or "
                                 "(nchan, 3)")
            nchan = xyz.shape[0]
            if xyz.shape[1] == 2:
                xyz = np.c_[xyz, np.zeros((nchan), dtype=np.float)]
            xyz[:, 2] = 1.
            keeponly = np.ones((xyz.shape[0],), dtype=bool)
            channels = [''] * nchan if channels is None else channels
            auto = True
        elif (xyz is None) and (channels is not None):  # channels exist
            if all([isinstance(k, str) for k in channels]):
                xyz, keeponly = self._get_coordinates_from_name(channels)
                system, unit = 'spherical', 'degree'
                auto = False

        # Select channels to use :
        if any(keeponly):
            if not all(keeponly):
                ignore = list(np.array(channels)[np.invert(keeponly)])
                logger.warning("Ignored channels for topoplot :"
                               " %s" % ', '.join(ignore))

            # ----------- Conversion -----------
            if isinstance(xyz, np.ndarray):
                if system == 'cartesian':
                    pass  # all good
                elif system == 'spherical':
                    xyz = self._spherical_to_cartesian(xyz, unit)
                    xyz = self.array_project_radial_to3d(xyz)

        self._xyz = xyz
        self._channels = channels
        self._keeponly = keeponly
        self._nchan = len(channels)

        return auto

    def _get_ref_coordinates(self, x='T4', y='Fpz'):
        """Get cartesian coordinates for electrodes to use as references.

        The ELAN software use by default spherical coordinates with T4 as the
        extrema for the x-axis and Fpz as the extrema for the y-axis.

        Parameters
        ----------
        x : string | 'T4'
            Name of the electrode t use as a reference for the x-axis.
        y : string | 'Fpz'
            Name of the electrode t use as a reference for the y-axis.
        """
        ref = self._get_coordinates_from_name([x, y])[0]
        ref = self._spherical_to_cartesian(ref, unit='degree')
        ref = self.array_project_radial_to3d(ref)
        ref_x, ref_y = ref[0, 0], ref[1, 1]
        return ref_x, ref_y

    @staticmethod
    def _get_coordinates_from_name(chan):
        """From the name of the channels, find xyz coordinates.

        Parameters
        ----------
        chan : list
            List of channel names.
        """
        # Load the coordinates template :
        path = download_file('eegref.npz', astype='topo')
        file = np.load(path)
        name_ref, xyz_ref = file['chan'], file['xyz']
        keeponly = np.ones((len(chan)), dtype=bool)
        # Find and load xyz coordinates :
        xyz = np.zeros((len(chan), 3), dtype=np.float32)
        for num, k in enumerate(chan):
            # Find if the channel is present :
            idx = np.where(name_ref == k.lower())[0]
            if idx.size:
                xyz[num, 0:2] = np.array(xyz_ref[idx[0], :])
            else:
                keeponly[num] = False

        return np.array(xyz), keeponly

    @staticmethod
    def _spherical_to_cartesian(xyz, unit='rad'):
        """Convert spherical coordinates to cartesian.

        Parameters
        ----------
        xyz : array_like
            The array of spheric coordinate of shape (N, 3).
        unit : {'rad', 'degree'}
            Specify the unit angles.

        Returns
        -------
        xyz : array_like
            The cartesian coordinates of the angle of shape (N, 3).
        """
        # Get theta / phi :
        theta, phi = xyz[:, 0], xyz[:, 1]
        if unit is 'degree':
            np.deg2rad(theta, out=theta)
            np.deg2rad(phi, out=phi)
        # Get radius :
        r = np.sin(theta)
        # Get cartesian coordinates :
        np.multiply(np.cos(phi), r, out=xyz[:, 0])
        np.multiply(np.sin(phi), r, out=xyz[:, 1])
        np.cos(theta, xyz[:, 2])
        return xyz

    @staticmethod
    def _griddata(x, y, v, xi, yi):
        """Make griddata."""
        xy = x.ravel() + y.ravel() * -1j
        d = xy[None, :] * np.ones((len(xy), 1))
        d = np.abs(d - d.T)
        n = d.shape[0]
        d.flat[::n + 1] = 1.

        g = (d * d) * (np.log(d) - 1.)
        g.flat[::n + 1] = 0.
        weights = np.linalg.solve(g, v.ravel())

        m, n = xi.shape
        zi = np.zeros_like(xi)
        xy = xy.T

        g = np.empty(xy.shape)
        for i in range(m):
            for j in range(n):
                d = np.abs(xi[i, j] + -1j * yi[i, j] - xy)
                mask = np.where(d == 0)[0]
                if len(mask):
                    d[mask] = 1.
                np.log(d, out=g)
                g -= 1.
                g *= d * d
                if len(mask):
                    g[mask] = 0.
                zi[i, j] = g.dot(weights)
        return zi

    @staticmethod
    def array_project_radial_to3d(points_2d):
        """Radial 3d projection."""
        points_2d = np.atleast_2d(points_2d)
        alphas = np.sqrt(np.sum(points_2d**2, -1))

        betas = np.sin(alphas) / alphas
        betas[alphas == 0] = 1
        x = points_2d[..., 0] * betas
        y = points_2d[..., 1] * betas
        z = np.cos(alphas)

        points_3d = np.asarray([x, y, z]).T

        return points_3d
