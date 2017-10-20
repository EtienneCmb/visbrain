"""Main class for Visbrain objects."""
import sys

import vispy
import vispy.visuals.transforms as vist

from .scene_obj import VisbrainCanvas
from ..utils import color2vb


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

    def __init__(self, name, parent=None, transform=None):
        """Init."""
        self._node = vispy.scene.Node(name=name)
        self._node.parent = parent
        # Name :
        assert isinstance(name, str)
        self._name = name
        # Transformation :
        if transform is None:
            transform = vist.NullTransform()
        self._node.transform = transform

    def __repr__(self):
        """Represent ClassName(name='object_name')."""
        return type(self).__name__ + "(name='" + self._name + "')"

    def __str__(self):
        """Return the object name."""
        return self._name

    def preview(self, bgcolor='white', axis=False, show=True):
        """Previsualize the result.

        Parameters
        ----------
        bgcolor : array_like/string/tuple | 'white'
            Background color for the preview.
        """
        parent_bck = self._node.parent
        canvas = VisbrainCanvas(axis=axis, show=show, name=self._name,
                                bgcolor=color2vb(bgcolor))
        self._node.parent = canvas.wc.scene
        canvas.camera = self._get_camera()
        # vispy.scene.visuals.XYZAxis(parent=canvas.wc.scene)
        # view.camera = camera
        if (sys.flags.interactive != 1) and show:
            vispy.app.run()
        # Reset orignial parent :
        self._node.parent = parent_bck

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
