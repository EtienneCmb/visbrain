"""Usefull functions for graphical interface managment."""

from PyQt5 import QtCore

import numpy as np

from .color import color2vb, color2tuple

__all__ = ('slider2opacity', 'textline2color', 'color2json',
           'ndsubplot', 'combo', 'is_color', 'MouseEventControl',
           'disconnect_all', 'extend_combo_list', 'get_combo_list_index',
           'safely_set_cbox', 'safely_set_spin', 'safely_set_slider',
           'toggle_enable_tab', 'get_screen_size', 'set_widget_size',
           'fill_pyqt_table')


def slider2opacity(value, thmin=0.0, thmax=100.0, vmin=-5.0, vmax=105.0,
                   tomin=-1000.0, tomax=1000.0):
    """Convert a slider value into opacity.

    Parameters
    ----------
    value : float
        The slider value
    thmin : float | 0.0
        Minimum threshold to consider
    thmax : float | 100.0
        Maximum threshold to consider
    tomin : float | -1000.0
        Set to tomin if value is under vmin
    tomax : float | 1000.0
        Set to tomax if value is over vmax

    Returns
    -------
    color : array_like
        Array of RGBA colors
    """
    alpha = 0.
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

    Parameters
    ----------
    value : string
        The edited string

    Returns
    -------
    value : string
        The processed string value.
    color : tuple
        Tuple of RGBA colors
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

    Parameters
    ----------
    obj : PyQt textline object
        The PyQt text line object.
    rmalpha : bool | True
        Specify if the alpha component have to be deleted.

    Returns
    -------
    coltuple : tuple
        A json compatible tuple of floating points.
    """
    return color2tuple(textline2color(obj.text())[1], float, rmalpha)


def is_color(color, comefrom='color'):
    """Test if a variable is a color.

    Parameters
    ----------
    color : str/tuple/list/array
        The color to test.
    comefrom : string | 'color'
        Where come from the color object. Use either 'color' if it has to
        be considered directly as a color or 'textline' if it comes from a
        textline gui objects.

    Returns
    -------
    iscol : bool
        A boolean value to indicate if it is a color.
    """
    if comefrom is 'color':
        try:
            color2vb(color)
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
            color2vb(color=color)
            iscol = True
        except:
            iscol = False
    else:
        raise ValueError("The comefrom must either be 'color' or 'textline'.")

    return iscol


def ndsubplot(n, line=4, force_col=None, max_rows=100, max_on_line=True):
    """Get the optimal number of rows / columns for a given integer.

    Parameters
    ----------
    n : int
        The length to convert into rows / columns.
    line : int | 4
        If n <= line, the number of rows will be forced to be 1.
    force_col : int | None
        Force the number of columns.
    max_rows : int | 10
        Maximum number of rows.
    max_on_line : bool | True
        Force to have the maximum set for lines.

    Returns
    -------
    nrows : int
        The number of rows.
    ncols : int
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

    if max_on_line and nrows < ncols:
        nrows, ncols = (ncols, nrows)

    return nrows, ncols


def combo(lst, idx):
    """Manage combo box.

    Parameters
    ----------
    lst : list
        List of possible values.
    idx : list
        List of index of several combo box.

    Returns
    -------
    out : list
        List of possible values for each combo box.
    ind : list
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

    def _is_left_click(self, event):
        """Return if the pressed button is the left one."""
        return event.button == 1

    def _is_modifier(self, event, modifier):
        """Return the name of the modifier use."""
        try:
            return event.modifiers[0].name == modifier
        except:
            return False


def disconnect_all(obj):
    """Disconnect all functions related to an PyQt object.

    Parameters
    ----------
    obj : PyQt object
        The PyQt object to disconnect.
    """
    while True:
        try:
            obj.disconnect()
        except TypeError:
            break


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
    """Get index of an item in a combo box.

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


def safely_set_cbox(cbox, idx, fcn=None):
    """Set QtComboBox list index without trigger.

    Parameters
    ----------
    cbox : PyQt.QtComboList
        The PyQt combo list object.
    idx : float/string
        Index or name of the item.
    fcn : list | None
        List of functions to disconnect then reconnect.
    """
    if isinstance(fcn, list):
        disconnect_all(cbox)
    if isinstance(idx, str):
        idx = get_combo_list_index(cbox, idx)
    cbox.setCurrentIndex(idx)
    if isinstance(fcn, list):
        for k in fcn:
            cbox.currentIndexChanged.connect(k)


def safely_set_spin(spin, value, fcn, keyboard_tracking=True):
    """Set value to QtSpin without trigger.

    Parameters
    ----------
    spin : QtSpin
        The Qt spin object.
    value : float
        Value to set.
    fcn : function
        List of function to reconnect.
    keyboard_tracking : bool | True
        Trigger while pressing values on keyboard.
    """
    # Disconnect and set value :
    disconnect_all(spin)
    spin.setValue(value)
    # Reconnect :
    for k in fcn:
        spin.valueChanged.connect(k)
    spin.setKeyboardTracking(False)


def safely_set_slider(slider, value, fcn):
    """Set value to QtSlider without trigger.

    Parameters
    ----------
    slider : QtSlider
        The Qt slider object.
    value : float
        Value to set.
    fcn : function
        List of function to reconnect.
    """
    # Disconnect and set value :
    disconnect_all(slider)
    slider.setValue(value)
    # Reconnect :
    for k in fcn:
        slider.sliderMoved.connect(k)


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


def get_screen_size(app):
    """Get screen size of an application.

    Parameters
    ----------
    app : QtApplication
        A PyQt application.

    Returns
    -------
    width : int
        Width of the application.
    height : int
        Height of the application.
    """
    resolution = app.desktop().screenGeometry()
    return resolution.width(), resolution.height()


def set_widget_size(app, widget, width=100., height=100.):
    """Set widget size proportionaly to screen resolution.

    Parameters
    ----------
    app : QtApplication
        A PyQt application.
    widget : QtWidget
        The PyQt widget.
    width : float | 100.
        Proportional width (0 < width <= 100).
    height : float | 100.
        Proportional height (0 < height <= 100).
    """
    # Check width and height :
    if not 0. < width <= 100.:
        raise ValueError("The width parameter must be 0 < width <= 100")
    if not 0. < height <= 100.:
        raise ValueError("The height parameter must be 0 < height <= 100")
    # Get scren (width, height) :
    s_width, s_height = get_screen_size(app)
    # Convert (width, height) into pixels :
    s_width = np.around(s_width * width / 100.)
    s_height = np.around(s_height * height / 100.)
    # Set maximum size to the widget :
    size = QtCore.QSize(s_width, s_height)
    widget.resize(size)


def fill_pyqt_table(table, col_names=None, col=None, df=None):
    """Fill a PyQt table widget.

    Parameters
    ----------
    col_names : list | None
        List of name of each columns.
    col : list | None
        List of columns values.
    df : pandas.DataFrame or dict | None
        Alternatively, a pandas DataFrame or a dictionary can also be used.
    """
    from PyQt5.QtWidgets import QTableWidgetItem

    # ________________________ Checking ________________________
    # Dictionary / pandas.DataFrame :
    if df is not None:
        col_names = list(df.keys())
        col = []
        for k in col_names:
            col.append(df[k])
    assert len(col_names) == len(col)
    assert all([isinstance(k, str) for k in col_names])

    # ________________________ Define table ________________________
    table.clear()
    table.setColumnCount(len(col_names))
    table.setHorizontalHeaderLabels(col_names)
    table.setRowCount(len(col[0]))

    # ________________________ Pre-allocate ________________________
    for i in range(table.rowCount()):
        for k in range(table.columnCount()):
            table.setItem(i, k, QTableWidgetItem(str(col[k][i])))
