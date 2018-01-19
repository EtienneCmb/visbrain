"""Topo class for topographic representations."""
import numpy as np

import vispy.scene.cameras as viscam
from vispy.scene import Node

from ..pyqt_module import PyQtModule
from .ui_init import UiInit
from .ui_elements import UiElements
from ..objects import ConnectObj
from ..visuals import TopoMesh, CbarVisual


__all__ = ('Topo')


class Topo(PyQtModule, UiInit, UiElements):
    """Display topographic representation."""

    def __init__(self, verbose=None):
        """Init."""
        PyQtModule.__init__(self, verbose=verbose, to_describe='_grid',
                            icon='topo_icon.svg', show_settings=False)
        self._topos = {}
        self._topoGrid = {}

        # ====================== App creation ======================
        UiInit.__init__(self)
        UiElements.__init__(self)

    def __getitem__(self, name):
        """Get the object name."""
        return self._topos[name]

    def __setitem__(self, name, value):
        """Set the object name."""
        self._topos[name] = value

    def add_topoplot(self, name, data, xyz=None, channels=None, c_connect=None,
                     c_select=None, c_cmap='inferno', c_linewidth=3.,
                     system='cartesian', unit='degree', title=None,
                     title_color='black', title_size=5., line_color='black',
                     line_width=2., chan_size=2., chan_offset=(0., 0., 0.),
                     chan_mark_color='white', chan_mark_symbol='disc',
                     chan_txt_color='black', bgcolor='white', cbar=True,
                     cblabel=None, cb_txt_size=4., levels=None,
                     level_colors='white', cmap='viridis', clim=None,
                     vmin=None, under='gray', vmax=None, over='red', row=0,
                     col=0, row_span=1, col_span=1, margin=.05):
        """Add a subplot embedded in a subplot.

        For now, there's two for using coordinates to define the subplot :

            * Using the xyz input (must either be in cartesian or spherical
              coordinate system)
            * Using the channel input. The Topo class contains a list of
              existing channel names and will try to identify those in the
              channels variable.

        Parameters
        ----------
        name : string
            Name of the topographic plot.
        data : array_like
            Array of data of shape (n_channels,).
        xyz : array_like | None
            Array of source's coordinates.
        channels : list | None
            List of channel names.
        c_connect : array_like | None
            Array of connections between sources. Must be a (n_channels,
            n_channels) upper triangular array of connecivity strength.
        c_select : array_like | None
            Array of boolean values to select which edges to display or to
            hide.
        c_cmap : string | 'inferno'
            Colormap name to use for the edges color.
        c_linewidth : float | 3.
            Connectivity edges line width.
        system : {'cartesian', 'spherical'}
            Coordinate system.
        unit : {'degree', 'rad'}
            If system is 'spherical', specify if angles are in degrees or
            radians.
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
        cblabel : string | None
            Colorbar label.
        cb_txt_size : float | 16.
            Text size for the colorbar limits and label.
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
        row : int | 0
            The row in which to add the widget (0 is the topmost row)
        col : int | 0
            The column in which to add the widget (0 is the leftmost column)
        row_span : int | 1
            The number of rows to be occupied by the topoplot.
        col_span : int | 1
            The number of columns to be occupied by the topoplot.
        margin : float | .05
            Margin percentage between the topoplot and the edge of the subplot.
        """
        # Check if name is available :
        self._check_name_for(name, 'topoplot')
        # Create the topoplot and set the data :
        topo = TopoMesh(xyz, channels, system, unit, title, title_color,
                        title_size, line_color, line_width, chan_size,
                        chan_offset, chan_mark_color, chan_mark_symbol,
                        chan_txt_color, bgcolor, cbar, cb_txt_size,
                        margin)
        topo.set_data(data, levels, level_colors, cmap, clim, vmin, under,
                      vmax, over, cblabel)
        # Connectivity :
        if isinstance(c_connect, np.ndarray):
            assert c_connect.shape == (len(topo), len(topo))
            xyz = topo._xyz[topo._keeponly]
            self.connect = ConnectObj('TopoConnect', xyz, c_connect,
                                      cmap=c_cmap, select=c_select,
                                      line_width=c_linewidth,
                                      parent=topo.node_chan)
        self[name] = topo
        # Create a PanZoom camera :
        cam = viscam.PanZoomCamera(aspect=1., rect=topo.rect)
        cam.set_default_state()
        # Create a subplot and add the camera :
        self._topoGrid[name] = self._grid.add_view(row, col, row_span,
                                                   col_span, bgcolor=bgcolor,
                                                   camera=cam)
        # Add the topoplot to the subplot :
        self._topoGrid[name].add(self[name].node)

    def add_shared_colorbar(self, name, cmap='viridis', clim=(0, 1), vmin=None,
                            vmax=None, under='gray', over='red', cblabel='',
                            cbtxtsz=5., cbtxtsh=2.3, txtcolor='black',
                            txtsz=3., txtsh=1.2, width=.17, border=True, bw=2.,
                            limtxt=True, bgcolor='white', ndigits=2, row=0,
                            col=0, row_span=1, col_span=1,
                            rect=(-1.2, -1.2, 2.4, 2.4)):
        """Add a shared colorbar across subplots.

        Parameters
        ----------
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
        cblabel : string | ''
            Colorbar label.
        cbtxtsz : float | 5..
            Text size of the colorbar label.
        cbtxtsh : float | 2.3
            Shift for the colorbar label.
        txtcolor : string | 'white'
            Text color.
        txtsz : float | 3.
            Text size for clim/vmin/vmax text.
        txtsh : float | 1.2
            Shift for clim/vmin/vmax text.
        border : bool | True
            Display colorbar borders.
        bw : float | 2.
            Border width.
        limtxt : bool | True
            Display vmin/vmax text.
        bgcolor : tuple/string | (0., 0., 0.)
            Background color of the colorbar canvas.
        ndigits : int | 2
            Number of digits for the text.
        row : int | 0
            The row in which to add the widget (0 is the topmost row)
        col : int | 0
            The column in which to add the widget (0 is the leftmost column)
        row_span : int | 1
            The number of rows to be occupied by the topoplot.
        col_span : int | 1
            The number of columns to be occupied by the topoplot.
        rect : tuple | (-1.2, -1.2, 2.4, 2.4)
            The 2-D area on the screen to display. The rect input describe
            (x_start, y_start, x_width, y_height). This variable can be used
            to translate or scale.
        """
        # Check if name is avaible :
        self._check_name_for(name, 'colorbar')
        # Create a PanZoom camera :
        cam = viscam.PanZoomCamera(rect=rect)
        cam.set_default_state()
        # Create a subplot and add the camera :
        self._topoGrid[name] = self._grid.add_view(row, col, row_span,
                                                   col_span, bgcolor=bgcolor,
                                                   camera=cam)
        # Get if vmin and vmax exist :
        isvmin, isvmax = vmin is not None, vmax is not None
        # Create a colorbar object :
        parent = Node(name=name)
        cbar = CbarVisual(cmap=cmap, clim=clim, vmin=vmin, isvmin=isvmin,
                          vmax=vmax, isvmax=isvmax, under=under, over=over,
                          cblabel=cblabel, cbtxtsz=cbtxtsz, cbtxtsh=cbtxtsh,
                          txtcolor=txtcolor, txtsz=txtsz, txtsh=txtsh,
                          width=width, border=border, bw=bw, limtxt=limtxt,
                          bgcolor=bgcolor, ndigits=ndigits, parent=parent)
        self[name] = cbar
        # Add the colorbar to the subplot :
        self._topoGrid[name].add(parent)

    def _check_name_for(self, name, use='topoplot'):
        """Check if the object name already exist."""
        if not isinstance(name, str):
            raise ValueError("name must be a string describing the name of the"
                             " " + use)
        elif name in list(self._topos.keys()):
            raise ValueError("'" + name + "' already exist. Use a different"
                             " name for this " + use + ".")
