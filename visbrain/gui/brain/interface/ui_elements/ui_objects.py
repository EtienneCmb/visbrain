"""Main class for the objects panel."""
from functools import wraps

from visbrain.utils import disconnect_all


def _run_method_if_needed(fn):
    @wraps(fn)
    def wrapper(self):
        if self._obj_run_method:
            fn(self)
    return wrapper


class UiObjects(object):
    """Objects control from the GUI."""

    def __init__(self):
        """Init."""
        # Obj type / name :
        self._obj_type_lst.currentIndexChanged.connect(self._fcn_obj_type)
        self._obj_name_lst.currentIndexChanged.connect(self._fcn_obj_name)
        self._obj_run_method = True

    def _fcn_obj_type(self):
        """Change object type."""
        idx_type = self._obj_type_lst.currentIndex()
        # Display the object tab :
        self._obj_stack.setCurrentIndex(idx_type)
        # Add object names :
        disconnect_all(self._obj_name_lst)
        self._obj_name_lst.clear()
        if idx_type == 0:    # Brain
            obj = self.atlas
        elif idx_type == 1:    # ROI
            obj = self.roi
        elif idx_type == 2:    # Volume
            obj = self.volume
        elif idx_type == 3:    # Cross-sections
            obj = self.cross_sec
        elif idx_type == 4:    # Sources
            obj = self.sources
        elif idx_type == 5:  # Connectivity
            obj = self.connect
        elif idx_type == 6:  # Time-series
            obj = self.tseries
        elif idx_type == 7:  # Pictures
            obj = self.pic
        elif idx_type == 8:  # Vectors
            obj = self.vectors
        self._obj_stack.setEnabled(obj.name is not None)
        self._obj_name_lst.setEnabled(idx_type > 3)
        if (idx_type > 3) and (obj.name is not None):
            self._obj_name_lst.addItems(obj.get_list_of_objects())
            self._fcn_obj_name()
            self._obj_name_lst.currentIndexChanged.connect(self._fcn_obj_name)

    def _fcn_obj_name(self):
        """Change object name."""
        idx_type = self._obj_type_lst.currentIndex()
        if idx_type == 4:    # Sources
            fcn = self._sources_to_gui
        elif idx_type == 5:  # Connectivity
            fcn = self._connect_to_gui
        elif idx_type == 6:  # time-series
            fcn = self._ts_to_gui
        elif idx_type == 7:  # pictures
            fcn = self._pic_to_gui
        elif idx_type == 8:  # vectors
            fcn = self._vec_to_gui
        # if idx_type > 4:
        self._obj_run_method = False
        fcn()
        self._obj_run_method = True

    def _get_select_object(self):
        """Get the select object."""
        idx_type = self._obj_type_lst.currentIndex()
        name = self._obj_name_lst.currentText()
        if name and idx_type == 4:  # Sources
            return self.sources[name]
        elif name and idx_type == 5:  # Connectivity
            return self.connect[name]
        elif name and idx_type == 6:  # Time-series
            return self.tseries[name]
        elif name and idx_type == 7:  # Pictures
            return self.pic[name]
        elif name and idx_type == 8:  # Vectors
            return self.vectors[name]
