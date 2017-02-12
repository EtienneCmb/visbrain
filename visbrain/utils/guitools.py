"""Usefull functions for graphical interface managment."""

import numpy as np
from .color import color2vb


__all__ = ['slider2opacity', 'textline2color', 'uiSpinValue',
           'ndsubplot', 'combo']


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
        value = value.replace("'", '')
        # Tuple/list :
        try:
            if isinstance(eval(value), (tuple, list)):
                value = eval(value)
        except:
            pass
        return value, color2vb(color=value)
    except:
        return 'w', (1, 1, 1, 1)


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


def ndsubplot(n, line=4, force_col=None, max_rows=10):
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
            nrows = int(n/ncols)
        else:
            vec = np.linspace(max_rows, 2, max_rows + 1,
                              endpoint=False).astype(int)
            nbool = [not bool(n % k) for k in vec]
            if any(nbool):
                ncols = vec[nbool.index(True)]
                nrows = int(n/ncols)

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
