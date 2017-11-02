"""Create a basic scene for objects."""
from vispy import scene

from ..utils import color2vb
from ..visuals import CbarVisual


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
        Label, title, axis and border color (only if axis=True).
    tick_font_size : float | 10.
        Size of ticks for the x and y-axis (only if axis=True).
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
    show : bool | False
        Show the canvas.
    """

    def __init__(self, axis=False, title=None, xlabel=None, ylabel=None,
                 title_font_size=15., axis_font_size=12., axis_color='black',
                 tick_font_size=10., name=None, x_height_max=80,
                 y_width_max=80, axis_label_margin=50, tick_label_margin=5,
                 rpad=20., bgcolor='white', add_cbar=False, cargs={}, xargs={},
                 yargs={}, cbargs={}, show=False, camera=None):
        """Init."""
        self._axis = axis
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._title_font_size = title_font_size
        self._axis_font_size = axis_font_size
        self._axis_color = axis_color
        self._tick_font_size = tick_font_size
        self._name = name
        self._x_height_max = x_height_max
        self._y_width_max = y_width_max
        self._axis_label_margin = axis_label_margin
        self._tick_label_margin = tick_label_margin
        self._bgcolor = bgcolor
        self._visible = show

        # ########################## MAIN CANVAS ##########################
        self.canvas = scene.SceneCanvas(keys='interactive', bgcolor=bgcolor,
                                        show=show, title=name, **cargs)

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
            self.wc = grid.add_view(row=1, col=1, camera=camera)
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
            self.wc = self.canvas.central_widget.add_view(camera=camera)

    def __bool__(self):
        """Return if there's an axis attached to the canvas."""
        return self._axis

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

    # ----------- PARENT -----------
    @property
    def parent(self):
        """Get the parent value."""
        return self.wc.scene

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
        if self and isinstance(value, bool):
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
        if self and isinstance(value, str):
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
        if self and isinstance(value, str):
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
        if self and isinstance(value, str):
            self._titleObj.text = value
            self._titleObj.update()
            self._title = value

    # ----------- CAMERA -----------
    @property
    def camera(self):
        """Get the camera value."""
        return self.wc.camera

    @camera.setter
    def camera(self, value):
        """Set camera value."""
        self._camera = value
        # Set camera to the main widget :
        self.wc.camera = value
        # Link transformations with axis :
        if self:
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
        if self:
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
        if self and isinstance(value, (int, float)):
            self._titleObj._text_visual.font_size = value
            self._title_font_size = value

    # ----------- LABEL_FONT_SIZE -----------
    @property
    def axis_font_size(self):
        """Get the axis_font_size value."""
        return self._axis_font_size

    @axis_font_size.setter
    def axis_font_size(self, value):
        """Set axis_font_size value."""
        if self and isinstance(value, (int, float)):
            self.xaxis.axis._axis_label.font_size = value
            self.yaxis.axis._axis_label.font_size = value
            self._axis_font_size = value

    # ----------- AXIS_FONT_SIZE -----------
    @property
    def tick_font_size(self):
        """Get the tick_font_size value."""
        return self._tick_font_size

    @tick_font_size.setter
    def tick_font_size(self, value):
        """Set tick_font_size value."""
        if self and isinstance(value, (int, float)):
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


class SceneObj(object):
    """Create a scene for objects.

    Parameters
    ----------
    bgcolor : string | 'black'
        Background color of the scene.
    """

    def __init__(self, bgcolor='black', show=True):
        """Init."""
        self._canvas = scene.SceneCanvas(keys='interactive', show=show,
                                         title='Object scene',
                                         bgcolor=color2vb(bgcolor))
        self._grid = self._canvas.central_widget.add_grid(margin=10)

    def add_to_subplot(self, obj, row=0, col=0):
        """Add object to subplot.

        Parameters
        ----------
        obj : visbrain.object
            The visbrain object to add.
        row : int | 0
            Row location for the object.
        col : int | 0
            Columns location for the object.
        """
        try:
            cam = obj._get_camera()
        except:
            cam = 'turntable'
        sub = self._grid.add_view(row=row, col=col, camera=cam)
        sub.add(obj.parent)
