"""Group of functions for plotting managment."""

import numpy as np

__all__ = ['ndsubplot']


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
