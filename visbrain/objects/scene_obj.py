"""Create a basic scene for objects."""
import sys
import logging

import numpy as np
from vispy import scene

from ..io import write_fig_canvas
from ..utils import color2vb, set_log_level, rotate_turntable
from ..visuals import CbarVisual
from ..config import CONFIG, PROFILER

logger = logging.getLogger('visbrain')


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
                 yargs={}, cbargs={}, show=False, camera=None, shortcuts={}):
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

            # ----------- LINK -----------
            self.xaxis.link_view(self.wc)
            self.yaxis.link_view(self.wc)

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
    """Create a scene and add objects to it.

    Parameters
    ----------
    bgcolor : string | 'black'
        Background color of the scene.
    show : bool | True
        Display the canvas.
    camera_state : dict | {}
        The default camera state to use.
    verbose : string
        Verbosity level.
    """

    def __init__(self, bgcolor='black', camera_state={}, verbose=None,
                 **kwargs):
        """Init."""
        set_log_level(verbose)
        logger.info("Scene creation")
        PROFILER('Scene creation')
        # Create the canvas and the grid :
        self.canvas = scene.SceneCanvas(keys='interactive', show=False,
                                        title='Object scene',
                                        bgcolor=color2vb(bgcolor), **kwargs)
        self._grid = self.canvas.central_widget.add_grid(margin=10)
        # Padding at (0, 0) :
        _rpad = self._grid.add_widget(row=0, col=0, row_span=1)
        _rpad.width_max = 20
        _rpad.height_max = 20
        self._grid.spacing = 0
        self._grid_desc = {}
        self._camera_state = camera_state
        # OpenGL f***** up with small objects. So we need rescale scenes :
        self._fix_gl = 100.

    def __getitem__(self, rowcol):
        """Get an element of the grid.

        Parameters
        ----------
        rowcol : tuple
            Tuple of two integers to get the subplot of the grid.
        """
        assert len(rowcol) == 2
        return self._grid[(rowcol[0] + 1, rowcol[1] + 1)]

    def _gl_uniform_transforms(self):
        """Check that transforms are uniforms inside the grid."""
        for k in self._grid.children:  # loop over viewbox
            for i in k.children:  # loop over sub-scenes
                objs, transforms = [], []
                for j in i.children:  # loop of visuals in the scene
                    # Don't consider the camera :
                    if not isinstance(j, scene.cameras.BaseCamera):
                        objs.append(j)
                        transforms.append(j.transform)
                        # Get scaling factor :
                        sc = np.array([k.scale.sum() for k in transforms])
                        if sc.size and not len(np.unique(sc)) == 1:
                            unique_tf = transforms[sc.argmax()]
                            for k in objs:
                                k.transform = unique_tf
                            logger.debug("Standardized transformations")

    def _gl_transform(self, obj):
        """Get the transformation to apply to the object."""
        if hasattr(obj, 'mesh'):
            logger.debug("Object rescaled %s" % str([self._fix_gl] * 3))
            obj._scale = self._fix_gl
            sc = [self._fix_gl] * 3
        else:
            sc = [1.] * 3
        # Add transformation to the node :
        if hasattr(obj, '_node'):  # VisbrainObject
            obj._node.transform = scene.transforms.STTransform(scale=sc)
        elif hasattr(obj, '_cnode'):  # combineObjects
            obj._cnode.transform = scene.transforms.STTransform(scale=sc)

    def add_to_subplot(self, obj, row=0, col=0, row_span=1, col_span=1,
                       title=None, title_size=12., title_color='white',
                       title_bold=True, use_this_cam=False, rotate=None,
                       camera_state={}, width_max=None, height_max=None):
        """Add object to subplot.

        Parameters
        ----------
        obj : visbrain.object
            The visbrain object to add.
        row : int | 0
            Row location for the object.
        col : int | 0
            Columns location for the object.
        row_span : int | 1
            Number of rows to use.
        col_span : int | 1
            Number of columns to use.
        title : string | None
            Subplot title.
        title_size : float | 12.
            Title font size.
        title_color : string/tuple/array_like | 'white'
            Color of the title.
        title_bold : bool | True
            Use bold title.
        use_this_cam : bool | False
            If you add multiple objects to the same scene and if you want to
            use the camera of an object as the reference, turn this parameter
            to True.
        rotate : string | None
            Rotate the scene. Use 'top', 'bottom', 'left', 'right', 'front' or
            'back'. Only available for 3-D objects.
        camera_state : dict | {}
            Arguments to pass to the camera.
        width_max : float | None
            Maximum width of the subplot.
        height_max : float | None
            Maximum height of the subplot.
        """
        # Apply to objects (GL issue for small mesh) :
        self._gl_transform(obj)
        title = '' if not isinstance(title, str) else title
        if (row + 1, col + 1) not in self._grid_desc.keys():
            # Get the camera and add view to the grid :
            cam = obj._get_camera()
            cam.set_default_state()
            sub = self._grid.add_view(row=row + 1, col=col + 1,
                                      row_span=row_span, col_span=col_span,
                                      camera=cam)
            self._grid_desc[(row + 1, col + 1)] = len(self._grid.children)
            title_color = color2vb(title_color)
            tit = scene.visuals.Text(title, color=title_color, anchor_x='left',
                                     bold=title_bold, font_size=title_size)
            sub.add_subvisual(tit)
        else:
            sub = self[(row, col)]
            if use_this_cam:
                sub.camera = obj._get_camera()
                sub.camera.set_default_state()
            # For objects that have a mesh attribute, pass the camera :
            if hasattr(obj, 'mesh'):
                obj.mesh.set_camera(sub.camera)
            if title:
                logger.error("A title is already set. '%s' ignored" % title)
        # Fix the (height, width) max of the subplot :
        sub.height_max = height_max
        sub.width_max = width_max
        sub.add(obj.parent)
        # Camera :
        if camera_state == {}:
            camera_state = self._camera_state
        if isinstance(sub.camera, scene.cameras.TurntableCamera):
            rotate_turntable(fixed=rotate, camera_state=camera_state,
                             camera=sub.camera)
        PROFILER('%s added to the scene' % repr(obj))
        logger.info('%s added to the scene' % repr(obj))

    def link(self, *args):
        """Link the camera of several objects of the scene.

        Parameters
        ----------
        args : list
            List of tuple describing subplot locations. Alternatively, use `-1`
            to link all cameras.

        Examples
        --------
        >>> # Link cameras of subplots (0, 0), (0, 1) and (1, 0)
        >>> sc.link((0, 0), (0, 1), (1, 0))
        """
        logger.info('Link cameras')
        if args[0] == -1:
            args = [(k[0] - 1, k[1] - 1) for k in self._grid_desc.keys()]
        assert len(args) > 1
        assert all([len(k) == 2 for k in args])
        cam_obj_1 = self[args[0]].camera
        for obj in args[1::]:
            cam_obj_1.link(self[obj].camera)
        PROFILER('Link cameras %s' % str(args))

    def screenshot(self, saveas, print_size=None, dpi=300.,
                   unit='centimeter', factor=None, region=None, autocrop=False,
                   bgcolor=None, transparent=False, line_width=1.):
        """Take a screeshot of the scene.

        By default, the rendered canvas will have the size of your screen.
        The screenshot() method provides two ways to increase to exported image
        resolution :

            * Using print_size, unit and dpi inputs : specify the size of the
              image at a specific dpi level. For example, you might want to
              have an (10cm, 15cm) image at 300 dpi.
            * Using the factor input : multiply the default image size by this
              factor. For example, if you have a (1920, 1080) monitor and if
              factor is 2, the exported image should have a shape of
              (3840, 2160) pixels.

        Parameters
        ----------
        saveas : str
            The name of the file to be saved. This file must contains a
            extension like .png, .tiff, .jpg...
        print_size : tuple | None
            The desired print size. This argument should be used in association
            with the dpi and unit inputs. print_size describe should be a tuple
            of two floats describing (width, height) of the exported image for
            a specific dpi level. The final image might not have the exact
            desired size but will try instead to find a compromize
            regarding to the proportion of width/height of the original image.
        dpi : float | 300.
            Dots per inch for printing the image.
        unit : {'centimeter', 'millimeter', 'pixel', 'inch'}
            Unit of the printed size.
        factor : float | None
            If you don't want to use the print_size input, factor simply
            multiply the resolution of your screen.
        region : tuple | None
            Select a specific region. Must be a tuple of four integers each one
            describing (x_start, y_start, width, height).
        autocrop : bool | False
            Automaticaly crop the figure in order to have the smallest
            space between the brain and the border of the picture.
        bgcolor : array_like/string | None
            The background color of the image.
        transparent : bool | False
            Specify if the exported figure have to contains a transparent
            background.
        """
        kwargs = dict(print_size=print_size, dpi=dpi, factor=factor,
                      autocrop=autocrop, unit=unit, region=region,
                      bgcolor=bgcolor, transparent=transparent)
        self._gl_uniform_transforms()
        write_fig_canvas(saveas, self.canvas,
                         widget=self.canvas.central_widget, **kwargs)

    def preview(self):
        """Previsualize the result."""
        self._gl_uniform_transforms()
        self.canvas.show(visible=True)
        if PROFILER and logger.level == 1:
            logger.profiler("PARENT TREE \n%s" % self._grid.describe_tree())
            logger.profiler(" ")
            PROFILER.finish()
        if sys.flags.interactive != 1:
            CONFIG['VISPY_APP'].run()
