"""Usefull functions for graphical interface managment."""

import numpy as np
from vispy.scene import visuals

from .color import color2vb, color2tuple


__all__ = ('slider2opacity', 'textline2color', 'color2json', 'uiSpinValue',
           'ndsubplot', 'combo', 'is_color', 'MouseEventControl', 'GuideLines',
           'extend_combo_list', 'get_combo_list_index', 'toggle_enable_tab')


def slider2opacity(value, thmin=0.0, thmax=100.0, vmin=-5.0, vmax=105.0,
                   tomin=-1000.0, tomax=1000.0):
    """Convert a slider value into opacity.

    Args:
        value: float
            The slider value

    Kargs:
        thmin: float, optional, (def: 0.0)
            Minimum threshold to consider

        thmax: float, optional, (def: 100.0)
            Maximum threshold to consider

        tomin: float, optional, (def: -1000.0)
            Set to tomin if value is under vmin

        tomax: float, optional, (def: 1000.0)
            Set to tomax if value is over vmax

    Return:
        color: array
            Array of RGBA colors
    """
    alpha = 0.0
    # Linear decrease :
    if value < thmin:
        alpha = value * tomin / vmin
    # Linear increase :
    elif value > thmax:
        alpha = value * tomax / vmax
    else:
        alpha = value / 100
    return alpha


def textline2color(value):
    """Transform a Qt text line editor into color.

    Args:
        value: string
            The edited string

    Return:
        The processed value

        tuple of RGBA colors
    """
    # Remove ' caracter :
    try:
        value = value.replace("'", '').strip()
        # Tuple/list :
        try:
            if isinstance(eval(value), (tuple, list)):
                value = eval(value)
        except:
            pass
        return value, color2vb(color=value)
    except:
        return 'white', (1., 1., 1., 1.)


def color2json(obj, rmalpha=True):
    """Turn a color textline into a json compatible one.

    Args:
        obj: PyQt textline object
            The PyQt text line object.

    Kargs:
        rmalpha: bool, optional, (def: True)
            Specify if the alpha component have to be deleted.

    Returns:
        coltuple: tuple
            A json compatible tuple of floating points.
    """
    return color2tuple(textline2color(obj.text())[1], float, rmalpha)


def is_color(color, comefrom='color'):
    """Test if a variable is a color.

    Args:
        color: str/tuple/list/array
            The color to test.

    Kargs:
        comefrom: string, optional, (def: 'color')
            Where come from the color object. Use either 'color' if it has to
            be considered directly as a color or 'textline' if it comes from a
            textline gui objects.

    Returns:
        iscol: bool
            A boolean value to indicate if it is a color.
    """
    if comefrom is 'color':
        try:
            _ = color2vb(color)
            iscol = True
        except:
            iscol = False
    elif comefrom is 'textline':
        try:
            color = color.replace("'", '')
            try:
                if isinstance(eval(color), (tuple, list)):
                    color = eval(color)
            except:
                pass
            _ = color2vb(color=color)
            iscol = True
        except:
            iscol = False
    else:
        raise ValueError("The comefrom must either be 'color' or 'textline'.")

    return iscol


def uiSpinValue(elements, values):
    """Set a list of value to a list of elements.

    Args:
        elements: QtSpin
            List of qt spin elements

        values: list
            List of values per element
    """
    if len(elements) != len(values):
        raise ValueError("List of Qt spins must have the same length "
                         "as values")
    [k.setValue(i) for k, i in zip(elements, values)]


def ndsubplot(n, line=4, force_col=None, max_rows=100):
    """Get the optimal number of rows / columns for a given integer.

    Note

    Args:
        n: int
            The length to convert into rows / columns.

    Kargs:
        line: int, optional, (def: 4)
            If n <= line, the number of rows will be forced to be 1.

        force_col: int, optional, (def: None)
            Force the number of columns.

        max_rows: int, optional, (def: 10)
            Maximum number of rows.

    Returns:
        nrows: int
            The number of rows.

        ncols: int
            The number of columns.
    """
    # Force n to be integer :
    n = int(n)
    # Force to have a single line subplot :
    if n <= line:
        ncols, nrows = n, 1
    else:
        if force_col is not None:
            ncols = force_col
            nrows = int(n / ncols)
        else:
            # Build a linearly decreasing vector :
            vec = np.linspace(max_rows, 2, max_rows + 1,
                              endpoint=False).astype(int)
            # Compute n modulo each point in vec :
            mod, div = n % vec, n / vec
            # Find where the result is zero :
            nbool = np.invert(mod.astype(bool))
            if any(nbool):
                cmin = np.abs(vec[nbool] - div[nbool]).argmin()
                ncols = vec[nbool][cmin]
                nrows = int(n / ncols)
            else:
                nrows, ncols = 1, n

    return nrows, ncols


def combo(lst, idx):
    """Manage combo box.

    Args:
        lst: list
            List of possible values.

        idx: list
            List of index of several combo box.

    Returns:
        out: list
            List of possible values for each combo box.

        ind: list
            List of the new current index of each combo box.
    """
    out, ind, original = [], [], set(lst)
    for k in range(len(idx)):
        out.append(list(original.difference(idx[:k])))
        # ind.append(lst.index(idx[k]))
        ind.append(list(out)[k][0])
        # ind.append(out[k].index(idx[k]))
    return out, ind


class MouseEventControl(object):
    """Additional mouse control on VisPy canvas."""

    def _isLeftClick(self, event):
        """Return if the pressed button is the left one."""
        return event.button == 1

    def _isModifier(self, event, modifier):
        """Return the name of the modifier use."""
        try:
            return event.modifiers[0].name == modifier
        except:
            return False


def extend_combo_list(cbox, item, reconnect=None):
    """Extend a QtComboList with a new item.

    Parameters
    ----------
    cbox : PyQt.QtComboList
        The PyQt combo list object.
    item : string
        Name of the new item.
    reconnect : function | None
        The function to apply when the index changed.
    """
    # Get the list of current items and extend it :
    all_items = [cbox.itemText(i) for i in range(cbox.count())]
    all_items.append(item)
    # Reconnect function :
    is_connected = reconnect is not None
    # Disconnect if connected :
    if is_connected:
        cbox.disconnect()
    # Clear and safely add items :
    cbox.clear()
    cbox.addItems(all_items)
    # Reconnect if connected :
    if is_connected:
        cbox.currentIndexChanged.connect(reconnect)


def get_combo_list_index(cbox, name):
    """Extend a QtComboList with a new item.

    Parameters
    ----------
    cbox : PyQt.QtComboList
        The PyQt combo list object.
    name : string
        Name of the item.

    Returns
    -------
    index : int
        Index of the item in the combo box.
    """
    # Get the list of current items and extend it :
    all_items = [cbox.itemText(i) for i in range(cbox.count())]
    return all_items.index(name)


def toggle_enable_tab(tab, name, enable=False):
    """Enable or disable a tab based on the name.

    Parameters
    ----------
    tab : PyQt.QTabWidget
        The PyQt tab.
    name : string
        Name of the tab.
    enable : bool | False
        Enable or disble the tab.
    """
    # Get all tab names :
    names = [tab.tabText(k) for k in range(tab.count())]
    # Get index of named tab :
    idx = names.index(name)
    # Set tab enable/disable :
    tab.setTabEnabled(idx, enable)


class GuideLines(object):
    """Display GUI guidelines for screenshot.

    Args:
        size: tuple
            Size of the canvas.

    Kargs:
        parent: vispy, optional, (def: None)
            The guide lines parent.

        camrange: dict, optional, (def: None)
            Dictionary with the camera range.
    """

    def __init__(self, size, parent=None, color='#ab4642', camrange=None):
        """Init."""
        self.size = size
        self.range = camrange
        self.xm, self.xM = self.range['x'][0], self.range['x'][1]
        self.ym, self.yM = self.range['y'][0], self.range['y'][1]
        # Create line object :
        # pos = np.zeros((2, 2), dtype=np.float32)
        pos = np.random.rand(100, 3)
        self.mesh = visuals.Line(pos=pos, parent=parent, connect='segments',
                                 color=color)
        self.mesh.visible = False

    def set_data(self, crop=None):
        """"""
        self.xm, self.xM = self.range['x'][0], self.range['x'][1]
        self.ym, self.yM = self.range['y'][0], self.range['y'][1]
        # Get range :
        # crop = (0, 0, self.size[0], self.size[1])
        # Convert each value :
        cropXY = self._convert(crop[0], crop[1])
        cropHW = self._convert(crop[0] + crop[2], crop[1] + crop[3])
        # # Build segment :
        # segment = np.zeros((8, 3), dtype=np.float32)
        # segment[0, :] = (cropXY[0], cropXY[1], 0.)
        # segment[1, :] = (cropXY[0], cropHW[1], 0.)
        # segment[2, :] = (cropXY[0], cropHW[1], 0.)
        # segment[3, :] = (cropHW[0], cropHW[1], 0.)
        # segment[4, :] = (cropHW[0], cropHW[1], 0.)
        # segment[5, :] = (cropHW[0], cropXY[1], 0.)
        # segment[6, :] = (cropHW[0], cropXY[1], 0.)
        # segment[7, :] = (cropXY[0], cropXY[1], 0.)
        segment = np.array([
                           [-154., -100., 0.],
                           [154., 100., 0.]
                           ])
        self.mesh.set_data(pos=segment)

    def _convert(self, x, y):
        xc = self.xm + ((self.xM - self.xm) * x / self.size[0])
        yc = self.ym + ((self.yM - self.ym) * y / self.size[1])
        return xc, yc

    # ----------- RANGE -----------
    @property
    def range(self):
        """Get the range value."""
        return self._range

    @range.setter
    def range(self, value):
        """Set range value."""
        self._range = value
        self.xm, self.xM = self.range['x'][0], self.range['x'][1]
        self.ym, self.yM = self.range['y'][0], self.range['y'][1]
