"""Main class for Visbrain objects."""
import sys
import logging

import vispy
import vispy.visuals.transforms as vist

from .scene_obj import VisbrainCanvas
from ..io import write_fig_canvas
from ..utils import color2vb, set_log_level
from ..config import VISPY_APP

logger = logging.getLogger('visbrain')


class VisbrainObject(object):
    """Base class inherited by all of the Visbrain objects.

    Parameters
    ----------
    name : string
        Object name.
    parent : VisPy.parent | None
        Markers object parent.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    """

    def __init__(self, name, parent=None, transform=None, verbose=None):
        """Init."""
        self._node = vispy.scene.Node(name=name)
        self._node.parent = parent
        self._csize = None  # canvas size
        # Name :
        assert isinstance(name, str)
        self._name = name
        # Transformation :
        if transform is None:
            transform = vist.NullTransform()
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

    def _get_parent(self, bgcolor, axis, show):
        """Get the object parent for preview and screenshot."""
        camera = self._get_camera()
        canvas = VisbrainCanvas(axis=axis, show=show, name=self._name,
                                bgcolor=color2vb(bgcolor), camera=camera)
        self._csize = canvas.canvas.size
        self._node.parent = canvas.wc.scene
        return canvas

    def preview(self, bgcolor='white', axis=False, xyz=False, show=True):
        """Previsualize the result.

        Parameters
        ----------
        bgcolor : array_like/string/tuple | 'white'
            Background color for the preview.
        axis : bool | False
            Add x and y axis with ticks.
        xyz : bool | False
            Add an (x, y, z) axis to the scene.
        """
        parent_bck = self._node.parent
        canvas = self._get_parent(bgcolor, axis, show)
        if xyz:
            vispy.scene.visuals.XYZAxis(parent=canvas.wc.scene)
        # view.camera = camera
        if (sys.flags.interactive != 1) and show:
            VISPY_APP.run()
        # Reset orignial parent :
        self._node.parent = parent_bck

    def describe_tree(self):
        """Tree description."""
        return self._node.describe_tree()

    def screenshot(self, saveas, print_size=None, dpi=300.,
                   unit='centimeter', factor=None, region=None, autocrop=False,
                   bgcolor=None, transparent=False):
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
        canvas = self._get_parent(bgcolor, False, False)
        write_fig_canvas(saveas, canvas.canvas, **kwargs)
        self._node.parent = None

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


class CombineObjects(object):
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
