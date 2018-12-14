"""Main class for Visbrain objects."""
import os
import sys
import logging

import vispy
import vispy.visuals.transforms as vist

from .scene_obj import VisbrainCanvas
from ..io import (write_fig_canvas, dialog_save, path_to_visbrain_data,
                  load_config_json, get_data_url_path, download_file,
                  get_files_in_folders, mpl_preview)
from ..utils import color2vb, set_log_level, merge_cameras
from ..config import CONFIG
from ..visuals import CbarBase

logger = logging.getLogger('visbrain')


class _VisbrainShortcuts(object):
    """Add shortcuts to a canvas."""

    def __init__(self):
        """Init."""
        self.key_press = {}
        self.events = ['mouse_release', 'mouse_double_click', 'mouse_move',
                       'mouse_press']

    def set_shortcuts_to_canvas(self, canvas):
        """Set shortcuts to a VisbrainCanvas."""
        assert isinstance(canvas, VisbrainCanvas)
        self.canvas = canvas
        ce = canvas.canvas.events  # noqa
        for k in self.events:
            if hasattr(self, '_on_' + k):
                eval('ce.%s.connect(self._on_%s())' % (k, k))
        # Key-pressed :

        def _save_canvas(event):
            from PyQt5.QtWidgets import QWidget
            ext = ['png', 'tiff', 'jpg']
            _ext = ['%s file (*.%s)' % (k.upper(), k) for k in ext]
            _ext += ['All files (*.*)']
            saveas = dialog_save(QWidget(), name='Export the scene',
                                 default='canvas.png', allext=_ext)
            if saveas:
                write_fig_canvas(saveas, self.canvas.canvas,
                                 widget=self.canvas.canvas.central_widget)
        self.key_press['s'] = _save_canvas

        def _fcn_key_press(event):
            """Key pressed."""
            if event.text in self.key_press.keys():
                self.key_press[event.text](event)
        ce.key_press.connect(_fcn_key_press)


class _VisbrainObj(CbarBase, _VisbrainShortcuts):
    """Class for VisbrainObjects and CombineObjects."""

    def __init__(self, **kw):
        """Init."""
        CbarBase.__init__(self, **kw)
        _VisbrainShortcuts.__init__(self)
        self._default_cblabel = ''
        self._data_folder = None

    # --------------------------- CAMERA ---------------------------
    def _get_camera(self):
        raise NotImplementedError

    # --------------------------- COLORBAR ---------------------------
    def _update_cbar(self):
        raise NotImplementedError

    def _update_cbar_minmax(self):
        raise NotImplementedError

    # --------------------------- DATA ---------------------------
    def _df_is_downloadable(self, file):
        """Get if a file name could be downloaded."""
        json_path = get_data_url_path()
        json_struct = load_config_json(json_path)[self._data_folder]
        return file in json_struct

    def _df_is_downloaded(self, file):
        """Get if a file has already been downloaded."""
        return os.path.isfile(os.path.join(self._data_folder_path, file))

    def _df_get_downloadable(self):
        """Get the list of files that can be downloaded."""
        json_path = get_data_url_path()
        return load_config_json(json_path)[self._data_folder]

    def _df_get_tmp_folder(self):
        """Get the tmp associated folder."""
        vb_path = path_to_visbrain_data()
        return os.path.join(*(vb_path, 'tmp', self._data_folder))

    def _df_get_downloaded(self, **kwargs):
        """Get the list of files that are already downloaded."""
        main_path = get_files_in_folders(self._data_folder_path, **kwargs)
        tmp_path = self._df_get_tmp_folder()
        if os.path.isdir(tmp_path):
            main_path += get_files_in_folders(tmp_path, **kwargs)
        return main_path

    def _df_get_file(self, file, download=True):
        """Get the path to a file or download it if needed."""
        is_dl = self._df_is_downloaded(file)
        if not is_dl and download:
            assert self._df_is_downloadable(file)
            self._df_download_file(file)
        # Find if the file is in _data_folder or in tmp :
        if file in os.listdir(self._data_folder_path):
            use_path = self._data_folder_path
        else:
            use_path = self._df_get_tmp_folder()
        return os.path.join(use_path, file)

    def _df_download_file(self, file):
        """Download a file."""
        return download_file(file, astype=self._data_folder)

    # ----------- DATA_FOLDER -----------
    @property
    def data_folder(self):
        """Get the data_folder value."""
        return self._data_folder

    @data_folder.setter
    def data_folder(self, value):
        """Set data_folder value."""
        if isinstance(self._data_folder, str):
            raise ValueError("data_folder can only be set once.")
        assert isinstance(value, str)
        # Create the directory if it doesn't exist :
        full_path = path_to_visbrain_data(folder=value)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            logger.info("%s folder created" % full_path)
        self._data_folder = value
        self._data_folder_path = full_path


class VisbrainObject(_VisbrainObj):
    """Base class inherited by all of the Visbrain objects.

    Parameters
    ----------
    name : string
        Object name.
    parent : VisPy.parent | None
        Markers object parent.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    verbose : string
        Verbosity level.
    """

    def __init__(self, name, parent=None, transform=None, verbose=None, **kw):
        """Init."""
        _VisbrainObj.__init__(self, **kw)
        self._node = vispy.scene.Node(name=name)
        self._node.parent = parent
        self._csize = None  # canvas size
        self._shortcuts = {}
        # Name :
        assert isinstance(name, str)
        self._name = name
        # Transformation :
        if transform is None:
            transform = vist.STTransform()
        self._node.transform = transform
        # Verbose :
        set_log_level(verbose)
        logger.info('%s created' % repr(self))

    def __repr__(self):
        """Represent ClassName(name='object_name')."""
        return type(self).__name__ + "(name='" + self._name + "')"

    def __str__(self):
        """Return the object name."""
        return self._name

    def _get_parent(self, bgcolor, axis, show, obj=None, **kwargs):
        """Get the object parent for preview and screenshot."""
        if hasattr(obj, '_get_camera'):
            camera = obj._get_camera()
        else:
            camera = self._get_camera()
        canvas = VisbrainCanvas(axis=axis, show=show, name=self._name,
                                bgcolor=color2vb(bgcolor), camera=camera,
                                shortcuts=self._shortcuts, **kwargs)
        self._csize = canvas.canvas.size
        self.set_shortcuts_to_canvas(canvas)
        if not hasattr(self._node.parent, 'name'):
            self._node.parent = canvas.wc.scene
        return canvas

    def preview(self, bgcolor='black', axis=False, xyz=False, show=True,
                obj=None, size=(1200, 800), **kwargs):
        """Previsualize the result.

        Parameters
        ----------
        bgcolor : array_like/string/tuple | 'black'
            Background color for the preview.
        axis : bool | False
            Add x and y axis with ticks.
        xyz : bool | False
            Add an (x, y, z) axis to the scene.
        obj : VisbrainObj | None
            Pass a Visbrain object if you want to use the camera of an other
            object.
        size : tuple | (1200, 800)
            Default size of the window.
        kwargs : dict | {}
            Optional arguments are passed to the VisbrainCanvas class.
        """
        if CONFIG['MPL_RENDER']:
            canvas = self._get_parent(bgcolor, False, False, obj, **kwargs)
            mpl_preview(canvas.canvas, widget=canvas.canvas.central_widget)
        else:
            parent_bck = self._node.parent
            kwargs['cargs'] = {'size': size}
            canvas = self._get_parent(bgcolor, axis, show, obj, **kwargs)
            if xyz:
                vispy.scene.visuals.XYZAxis(parent=canvas.wc.scene)
            # view.camera = camera
            if (sys.flags.interactive != 1) and show:
                CONFIG['VISPY_APP'].run()
            # Reset orignial parent :
            self._node.parent = parent_bck

    def describe_tree(self):
        """Tree description."""
        return self._node.describe_tree()

    def animate(self, step=1., interval='auto', iterations=-1):
        """Animate the object.

        Note that this method can only be used with 3D objects.

        Parameters
        ----------
        step : float | 1.
            Rotation step.
        interval : float | 'auto'
            Time between events in seconds. The default is ‘auto’, which
            attempts to find the interval that matches the refresh rate of the
            current monitor. Currently this is simply 1/60.
        iterations : int | -1
            Number of iterations. Can be -1 for infinite.
        """
        from vispy.app import Timer
        def on_timer(*args, **kwargs):  # noqa
            if hasattr(self, 'camera'):
                self.camera.azimuth += step  # noqa
        kw = dict(connect=on_timer, app=CONFIG['VISPY_APP'],
                  interval=interval, iterations=iterations)
        self._app_timer = Timer(**kw)
        self._app_timer.start()

    def record_animation(self, name, n_pic=10, bgcolor=None):
        """Record an animated object and save as a *.gif file.

        Note that this method :

            * Can only be used with 3D objects.
            * Requires the python package imageio

        Parameters
        ----------
        name : string
            Name of the gif file (e.g 'myfile.gif')
        n_pic : int | 10
            Number of pictures to use to render the gif.
        bgcolor : string, tuple, list | None
            Background color.
        """
        import imageio
        writer = imageio.get_writer(name)
        canvas = self._get_parent(bgcolor, False, False)
        for k in range(n_pic):
            im = canvas.canvas.render()
            writer.append_data(im)
            self.camera.azimuth += 360. / n_pic
        writer.close()

    def screenshot(self, saveas, print_size=None, dpi=300., unit='centimeter',
                   factor=None, region=None, autocrop=False, bgcolor=None,
                   transparent=False, obj=None, line_width=1., **kwargs):
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
        obj : VisbrainObj | None
            Pass a Visbrain object if you want to use the camera of an other
            object for the sceen rendering.
        kwargs : dict | {}
            Optional arguments are passed to the VisbrainCanvas class.
        """
        kw = dict(print_size=print_size, dpi=dpi, factor=factor,
                  autocrop=autocrop, unit=unit, region=region,
                  bgcolor=bgcolor, transparent=transparent)
        canvas = self._get_parent(bgcolor, False, False, obj, **kwargs)
        write_fig_canvas(saveas, canvas.canvas,
                         widget=canvas.canvas.central_widget, **kw)
        self._node.parent = None

    def copy(self):
        """Get a copy of the object."""
        from copy import copy
        return copy(self)

    # ----------- PARENT -----------
    @property
    def parent(self):
        """Get the parent value."""
        p_isnn = self._node.parent is not None
        return self._node.parent if p_isnn else self._node

    @parent.setter
    def parent(self, value):
        """Set parent value."""
        self._node.parent = value

    # ----------- TRANSFORM -----------
    @property
    def transform(self):
        """Get the transform value."""
        return self._node.transform

    @transform.setter
    def transform(self, value):
        """Set transform value."""
        self._node.transform = value

    # ----------- NAME -----------
    @property
    def name(self):
        """Get the name value."""
        return self._name

    # ----------- VISIBLE_OBJ -----------
    @property
    def visible_obj(self):
        """Get the visible_obj value."""
        return self._node.visible

    @visible_obj.setter
    def visible_obj(self, value):
        """Set visible_obj value."""
        assert isinstance(value, bool)
        self._node.visible = value


class CombineObjects(_VisbrainObj):
    """Combine Visbrain objects.

    Parameters
    ----------
    obj_type : Object type
        The object type.
    objects : list or obj_type
        List of objects (or single object).
    """

    def __init__(self, obj_type, objects, select=None, parent=None):
        """Init."""
        _VisbrainObj.__init__(self)
        # Parent node for combined objects :
        self._cnode = vispy.scene.Node(name='Combine ' + obj_type.__name__)
        self._cnode.parent = parent
        # Initialize objects :
        self._objs, self._objs_order = {}, []
        self._visible_obj = True
        self._obj_type = obj_type.__name__
        if objects is not None:
            if isinstance(objects, obj_type):  # single object
                objects = [objects]
            if isinstance(objects, list):  # list of objects
                assert all([isinstance(k, obj_type) for k in objects])
                self._objs_order = [k.name for k in objects]
                self._objs = {k.name: k for k in objects}
            else:
                raise TypeError("Wrong object type. Can not combine objects.")
            # Select an object. By default, the first one is selected :
            select = self._objs_order[0] if select is None else select
            self.select(select)
            self.name = str(self)
            # Set parent :
            for k in self:
                k.parent = self._cnode
        else:
            self.name = None

    def __getitem__(self, value):
        """Get the object from the key value."""
        if isinstance(value, str):
            return self._objs[value]
        elif isinstance(value, int):
            return self._objs[self._objs_order[value]]

    def __setitem__(self, key, value):
        """Set an attribute of the selected object.."""
        exec('self[self._select].' + key + ' = value')

    def __len__(self):
        """Get the number of objects."""
        return len(self._objs_order)

    def __iter__(self):
        """Iterate over objects."""
        for k in self._objs_order:
            yield self[k]

    def __str__(self):
        """Get the name of all objects."""
        return ' + '.join(self._objs_order)

    def __repr__(self):
        """Represent combined objects."""
        reprs = [repr(k) for k in self]
        return type(self).__name__ + "(" + ", ".join(reprs) + ")"

    def _get_camera(self):
        """Return a merged version of cameras."""
        cams = []
        for k in self:
            cams.append(k._get_camera())
        return merge_cameras(*tuple(cams))

    def update(self):
        """Update every objects."""
        self._cnode.update()
        for k in self:
            k._node.update()
            k.update()

    def get_list_of_objects(self):
        """Get the list of defined objects."""
        return self._objs_order

    def get_selected_object(self):
        """Get the curently selected object."""
        return self._select

    def append(self, obj):
        """Add a new object."""
        assert type(obj).__name__ == self._obj_type
        self._objs_order.append(obj.name)
        self._objs[obj.name] = obj

    def select(self, name=None):
        """Select an object.

        Parameters
        ----------
        name : string | None
            Name of the object to select.
        """
        if name is not None:
            assert name in self._objs_order
            self._select = name

    def eval(self, name, method, *args, **kwargs):
        """Evaluate a method of a particular object.

        Parameters
        ----------
        name : string
            Name of the object.
        method : string
            Name of the method to evaluate.
        args and kwargs: arguments
            Arguments pass to the method to evaluate.
        """
        assert name in self._objs_order and isinstance(method, str)
        # Eval the method :
        exec('self[name].' + method + '(*args, **kwargs)')

    # ----------- PARENT -----------
    @property
    def parent(self):
        """Get the parent value."""
        return self._cnode.parent

    @parent.setter
    def parent(self, value):
        """Set parent value."""
        self._cnode.parent = value

    # ----------- VISIBLE_OBJ -----------
    @property
    def visible_obj(self):
        """Get the visible_obj value."""
        return self._visible_obj

    @visible_obj.setter
    def visible_obj(self, value):
        """Set visible_obj value."""
        assert isinstance(value, bool)
        self._cnode.visible = value
        self._visible_obj = value
