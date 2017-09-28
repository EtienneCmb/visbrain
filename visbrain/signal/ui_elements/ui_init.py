"""VisPy canvas initialization."""
import numpy as np
from PyQt5 import QtWidgets
from warnings import warn

from vispy import app, scene

from ...visuals import CbarVisual
from ..gui import Ui_MainWindow
from ...utils import color2vb


class VisbrainCanvas(object):
    """Create a canvas with an embeded axis.

    Parameters
    ----------
    axis : bool | False
        Add axis to canvas.
    title : string | None
        Title of the axis (only if axis=True).
    xlabel : string | None
        Label for the x-axis (only if axis=True).
    ylabel : string | None
        Label for the y-axis (only if axis=True).
    title_font_size : float | 15.
        Size of the title (only if axis=True).
    axis_font_size : float | 12.
        Size of x and y labels (only if axis=True).
    axis_color : array_like/string/tuple | 'black'
        Axis color (x and y axis).
    tick_font_size : float | 10.
        Size of ticks for the x and y-axis (only if axis=True).
    color : array_like/tuple/string | 'white'
        Label, title, axis and border color (only if axis=True).
    name : string | None
        Canvas name.
    x_height_max : float | 80
        Height max of the x-axis.
    y_width_max : float | 80
        Width max of the y-axis.
    axis_label_margin : float | 50
        Margin between axis and label.
    tick_label_margin : float | 5
        Margin between ticks and label.
    rpad : float | 20.
        Right padding (space between the right border of the axis and the end
        of the canvas).
    bgcolor : array_like/tuple/string | 'black'
        Background color of the canvas.
    cargs : dict | {}
        Further arguments to pass to the SceneCanvas class.
    xargs : dict | {}
        Further arguments to pass to the AxisWidget (x-axis).
    yargs : dict | {}
        Further arguments to pass to the AxisWidget (y-axis).
    """

    def __init__(self, axis=False, title=None, xlabel=None, ylabel=None,
                 title_font_size=15., axis_font_size=12., axis_color='black',
                 tick_font_size=10., color='black', name=None, x_height_max=80,
                 y_width_max=80, axis_label_margin=50, tick_label_margin=5,
                 rpad=20., bgcolor='white', add_cbar=False, cargs={}, xargs={},
                 yargs={}, cbargs={}):
        """Init."""
        self._axis = axis

        # ########################## MAIN CANVAS ##########################
        self.canvas = scene.SceneCanvas(keys='interactive', bgcolor=bgcolor,
                                        show=False, title=name, **cargs)

        # ########################## AXIS ##########################
        if axis:  # add axis to canvas
            # ----------- GRID -----------
            grid = self.canvas.central_widget.add_grid(margin=10)
            grid.spacing = 0

            # ----------- COLOR -----------
            axcol = color2vb(axis_color)
            kw = {'axis_label_margin': axis_label_margin,
                  'tick_label_margin': tick_label_margin,
                  'axis_font_size': axis_font_size, 'axis_color': axcol,
                  'tick_color': axcol, 'text_color': axcol,
                  'tick_font_size': tick_font_size}

            # ----------- TITLE -----------
            self._titleObj = scene.Label(title, color=axcol,
                                         font_size=title_font_size)
            self._titleObj.height_max = 40
            grid.add_widget(self._titleObj, row=0, col=0, col_span=2)

            # ----------- Y-AXIS -----------
            yargs.update(kw)
            self.yaxis = scene.AxisWidget(orientation='left', domain=(0, 129),
                                          axis_label=ylabel, **yargs)
            self.yaxis.width_max = y_width_max
            grid.add_widget(self.yaxis, row=1, col=0)

            # ----------- X-AXIS -----------
            xargs.update(kw)
            self.xaxis = scene.AxisWidget(orientation='bottom',
                                          axis_label=xlabel, **xargs)
            self.xaxis.height_max = x_height_max
            grid.add_widget(self.xaxis, row=2, col=1)

            # ----------- MAIN -----------
            self.wc = grid.add_view(row=1, col=1)
            self.grid = grid

            # ----------- CBAR -----------
            rpad_col = 0
            if add_cbar:
                self.wc_cbar = grid.add_view(row=1, col=2)
                self.wc_cbar.width_max = 150.
                self.cbar = CbarVisual(width=.2, parent=self.wc_cbar.scene)
                rpad_col += 1

            # ----------- RIGHT PADDING -----------
            self._rpad = grid.add_widget(row=1, col=2 + rpad_col, row_span=1)
            self._rpad.width_max = rpad

        else:  # Ignore axis
            self.wc = self.canvas.central_widget.add_view()

    def update(self):
        """Update canvas."""
        self.canvas.update()
        self.wc.update()
        if self._axis:
            self.xaxis.axis._update_subvisuals()
            self.yaxis.axis._update_subvisuals()
            self.grid.update()

    def set_default_state(self):
        """Set the default state of the camera."""
        self.camera.set_default_state()

    # ----------- VISIBLE -----------
    @property
    def visible(self):
        """Get the visible value."""
        return self._visible

    @visible.setter
    def visible(self, value):
        """Set visible value."""
        if isinstance(value, bool):
            self._visible = value
            self.canvas.show = value
            self.update()

    # ----------- VISIBLE_AXIS -----------
    @property
    def axis(self):
        """Get the axis value."""
        return self._axis

    @axis.setter
    def axis(self, value):
        """Set axis value."""
        if hasattr(self, 'xaxis') and isinstance(value, bool):
            self.xaxis.visible = value
            self.yaxis.visible = value
            self._titleObj.visible = value
            self._rpad.visible = value
            self._visible_axis = value
            self._axis = value

    # ----------- XLABEL -----------
    @property
    def xlabel(self):
        """Get the xlabel value."""
        return self._xlabel

    @xlabel.setter
    def xlabel(self, value):
        """Set xlabel value."""
        if isinstance(value, str) and hasattr(self, 'xaxis'):
            self.xaxis.axis.axis_label = value
            self.xaxis.axis._update_subvisuals()
            self._xlabel = value

    # ----------- YLABEL -----------
    @property
    def ylabel(self):
        """Get the ylabel value."""
        return self._ylabel

    @ylabel.setter
    def ylabel(self, value):
        """Set ylabel value."""
        if isinstance(value, str) and hasattr(self, 'yaxis'):
            self.yaxis.axis.axis_label = value
            self.yaxis.axis._update_subvisuals()
            self._ylabel = value

    # ----------- TITLE -----------
    @property
    def title(self):
        """Get the title value."""
        return self._title

    @title.setter
    def title(self, value):
        """Set title value."""
        if isinstance(value, str) and hasattr(self, '_titleObj'):
            self._titleObj.text = value
            self._titleObj.update()
            self._title = value

    # ----------- CAMERA -----------
    @property
    def camera(self):
        """Get the camera value."""
        return self._camera

    @camera.setter
    def camera(self, value):
        """Set camera value."""
        self._camera = value
        # Set camera to the main widget :
        self.wc.camera = value
        # Link transformations with axis :
        if self._axis:
            self.xaxis.link_view(self.wc)
            self.yaxis.link_view(self.wc)

    # ----------- AXIS_COLOR -----------
    @property
    def axis_color(self):
        """Get the axis_color value."""
        return self._axis_color

    @axis_color.setter
    def axis_color(self, value):
        """Set axis_color value."""
        self._axis_color = value
        col = color2vb(value)
        if self._axis:
            # Title :
            self._titleObj._text_visual.color = col
            # X-axis :
            self.xaxis.axis.axis_color = col
            self.xaxis.axis.tick_color = col
            self.xaxis.axis._text.color = col
            self.xaxis.axis._axis_label.color = col
            # Y-axis :
            self.yaxis.axis.axis_color = col
            self.yaxis.axis.tick_color = col
            self.yaxis.axis._text.color = col
            self.yaxis.axis._axis_label.color = col
            self.update()

    # ----------- TITLE_FONT_SIZE -----------
    @property
    def title_font_size(self):
        """Get the title_font_size value."""
        return self._title_font_size

    @title_font_size.setter
    def title_font_size(self, value):
        """Set title_font_size value."""
        if self._axis and isinstance(value, (int, float)):
            self._titleObj._text_visual.font_size = value
            self._title_font_size = value

    # ----------- LABEL_FONT_SIZE -----------
    @property
    def axis_font_size(self):
        """Get the axis_font_size value."""
        return self._label_font_size

    @axis_font_size.setter
    def axis_font_size(self, value):
        """Set axis_font_size value."""
        if self._axis and isinstance(value, (int, float)):
            self.xaxis.axis._axis_label.font_size = value
            self.yaxis.axis._axis_label.font_size = value
            self._axis_font_size = value

    # ----------- AXIS_FONT_SIZE -----------
    @property
    def tick_font_size(self):
        """Get the tick_font_size value."""
        return self.tick_font_size

    @tick_font_size.setter
    def tick_font_size(self, value):
        """Set tick_font_size value."""
        if self._axis and isinstance(value, (int, float)):
            self.xaxis.axis._text.font_size = value
            self.yaxis.axis._text.font_size = value
            self._tick_font_size = value

    # ----------- BGCOLOR -----------
    @property
    def bgcolor(self):
        """Get the bgcolor value."""
        return self._bgcolor

    @bgcolor.setter
    def bgcolor(self, value):
        """Set bgcolor value."""
        self._bgcolor = value
        self.canvas.bgcolor = color2vb(value)


class GridShortcuts(object):
    """Add shortcuts to grid canvas.

    Parameters
    ----------
    canvas : vispy canvas
        Vispy canvas to add the shortcuts.
    """

    def __init__(self, canvas):
        """Init."""
        self._sh_grid = [('Double click (grid canvas)', "Enlarge signal "
                          "under the mouse cursor"),
                         ]

        @canvas.events.key_press.connect
        def on_key_press(event):
            """Executed function when a key is pressed."""
            pass

        @canvas.events.mouse_double_click.connect
        def on_mouse_double_click(event):
            """Executed function when double click mouse over canvas."""
            n_rows, n_cols = self._grid._g_size
            rect = self._grid_canvas.camera.rect
            w_cols, w_rows = self._grid_canvas.canvas.size
            # Get camera limits :
            bottom, height = rect.bottom, rect.height
            left, width = rect.left, rect.width
            x, y = event.pos
            # Pass in the camera system [-1, 1]:
            x_cam = (width * (x / w_cols) + left) + 1.
            y_cam = (height * y / w_rows) + bottom + 1.
            # Get signal location :
            x_loc = int(np.ceil((n_cols / 2.) * x_cam) - 1.)
            y_loc = int(abs(np.ceil((n_rows / 2.) * y_cam) - 1))
            y_loc, x_loc = self._grid._convert_row_cols(y_loc, x_loc)
            # String conversion :
            if self._data.ndim == 2:
                lst = [str(x_loc)]
            elif self._data.ndim == 3:
                lst = [str(y_loc), str(x_loc)]
            lst.insert(self._signal._axis, ':')
            st = '(' + ', '.join(lst) + ')'
            # Try to set the signal
            try:
                # Get signal index :
                index = self._signal._get_signal_index(st)
                self._safely_set_index(index, True, True)
                if not self.actionSignal.isChecked():
                    self.actionSignal.setChecked(True)
                    self._fcn_menu_disp_signal()
            except:
                warn("No signal found at this position.")


class SignalShortcuts(object):
    """Add shortcuts to grid canvas.

    Parameters
    ----------
    canvas : vispy canvas
        Vispy canvas to add the shortcuts.
    """

    def __init__(self, canvas):
        """Init."""
        self._sh_sig = [('n (signal canvas)', 'Go to the next signal'),
                        ('b (signal canvas)', 'Go to the previous signal'),
                        ('Double click (signal canvas)', 'Insert annotation'),
                        ('g', 'Display / hide grid'),
                        ('s', 'Display / hide signal'),
                        ('<delete>', 'Reset the camera'),
                        ('CTRL + t', 'Display shortcuts'),
                        ('CTRL + d', 'Display / hide setting panel'),
                        ('CTRL + n', 'Take a screenshot'),
                        ('CTRL + q', 'Close Sleep graphical interface'),
                        ]

        @canvas.events.key_press.connect
        def on_key_press(event):
            """Executed function when a key is pressed."""
            if event.text.lower() == 'n':
                self._fcn_next_index()
            elif event.text.lower() == 'b':
                self._fcn_prev_index()

        @canvas.events.mouse_double_click.connect
        def on_mouse_double_click(event):
            """Executed function when double click mouse over canvas."""
            # Get event position and camera rectangle:
            x_pos, y_pos = event.pos
            rect = self._signal_canvas._camera.rect
            # Get right padding, canvas, title and wc size :
            cs = canvas.size
            ws = self._signal_canvas.wc.size
            rpad = self._signal_canvas._rpad.size[0]
            ts = self._signal_canvas._titleObj.size[1]
            # From x-pos, remove offset du to y-label and ticks :
            x_pos -= cs[0] - (ws[0] + rpad)
            # From y-pos, remove offset du to title :
            y_pos -= ts
            # Get position only if double-click inside the widget :
            if (x_pos >= 0) and (y_pos >= 0):
                # Get time :
                t_diff = rect.right - rect.left
                t = (t_diff * x_pos / ws[0]) + rect.left
                # Get amplitude :
                d_diff = rect.top - rect.bottom
                d = rect.top - (d_diff * y_pos / ws[1])
                # Take only two decimals :
                t, d = np.around((t, d), decimals=2)
            # Add annotation :
            self._annotate_event(str(self._signal), (t, d))


class UiInit(QtWidgets.QMainWindow, Ui_MainWindow, app.Canvas):
    """docstring for UiInit."""

    def __init__(self, **kwargs):
        """Init."""
        # Create the main window :
        super(UiInit, self).__init__(None)
        self.setupUi(self)

        # Canvas creation :
        cargs = {'size': (800, 600)}
        self._grid_canvas = VisbrainCanvas(axis=False, name='Grid',
                                           cargs=cargs, **kwargs)
        self._signal_canvas = VisbrainCanvas(axis=True, name='Signal',
                                             cargs=cargs, add_cbar=True,
                                             **kwargs)

        # Add canvas to layout :
        self._GridLayout.addWidget(self._grid_canvas.canvas.native)
        self._SignalLayout.addWidget(self._signal_canvas.canvas.native)

        # Initialize shortcuts :
        GridShortcuts.__init__(self, self._grid_canvas.canvas)
        SignalShortcuts.__init__(self, self._signal_canvas.canvas)
