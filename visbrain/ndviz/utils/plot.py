"""Group of functions for plotting managment."""

import numpy as np

__all__ = ['ndsubplot', 'combo']


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
            vec = np.linspace(max_rows, 0, max_rows + 1).astype(int)
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
