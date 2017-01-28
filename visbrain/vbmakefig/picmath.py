"""okok."""

import numpy as np

__all__ = ['picsize', 'piccomplete']


def picsize(shapes, interh=0, beforeh=0, afterh=0, interv=0, beforev=0,
            afterv=0):
    """Evaluate the size of a picture in the context of multiple pictures.

    

    Args:
        shapes: array of shape (N, M)
            Array containing the shape of each picture

    Kargs:
        interh: int, optional, (def: 0)
            Add an horizontal inter-space between each picture.

        beforeh: int, optional, (def: 0)
            Add an horizontal space before the first picture.

        afterh: int, optional, (def: 0)
            Add an horizontal space after the last picture.

        interv: int, optional, (def: 0)
            Add an vertical inter-space between each picture.

        beforev: int, optional, (def: 0)
            Add an vertical space before the first picture.

        afterv: int, optional, (def: 0)
            Add an vertical space after the last picture.

    Returns:
        index: list
            List of slices for each picture. Each slice specify
            where each picture start and finish.
    """
    shapes = np.array(shapes)

    # Height evaluation :
    htot, hpic = _piclen(shapes[:, 0], before=beforev, inter=interv,
                         after=afterv)

    # Width evaluation :
    wtot, wpic = _piclen(shapes[:, 1], before=beforeh, inter=interh,
                         after=afterh)

    return (htot, wtot), (hpic, wpic)


def _piclen(shapes, before=0, inter=0, after=0):
    """Evaluate the length of a vector by taking into account
    maximum values and space (before, inter and after).

    Args:
        shapes: array of shape (N,)
            Vector of lengths for each picture at a specific axis

    Kargs:
        inter: int, optional, (def: 0)
            Add an inter-space between each picture.

        before: int, optional, (def: 0)
            Add a space before the first picture.

        after: int, optional, (def: 0)
            Add a space after the last picture.

    Returns:
        piclentot: int
            The length of the future picture.

        piclen: int
            The length of each picture.
    """
    # Force shapes to be a vector :
    shapes = shapes.ravel().astype(int)

    # Get usefull variables :
    N = len(shapes)
    step = shapes.max()

    return before + N * step + (N-1) * inter + after, step


def piccomplete(pic, toshape, picposh='left', picposv='center',
                val=0):
    """Complete a picture with rows / columns so that it fits to a
    predefined larger shape.

    Args:
        pic: ndarray
            The actual picture to use

        toshape: tuple
            Tuple of intergers in order to define the fina shape.
            Note that the pic.shape has to be inferior or equal
            to toshape.

    Kargs:
        picposh: string, optional, (def: 'left')
            Horizontal position of the picture. Use either 'left',
            'right' or 'center'.

        picposv: string, optional, (def: 'center')
            Vertical position of the picture. Use either 'top',
            'bottom' or 'center'.

        val: int/float, optional, (def: 0)
            The value to use to complete the picture.

    Return:
        pictot: ndarray of shape toshape
            The completed version of the initial picture.
    """
    # Inputs checking :
    if not all([p <= t for p, t in zip(pic.shape, toshape)]):
        raise ValueError("The destination shape must be at least"
                         " >= to the initial shape")

    # Pre-allocate space for the final picture :
    pictot = np.full(toshape, val, dtype=pic.dtype)

    # Find vertical / horizontal filling index :
    indv = _dimcomplete(pic.shape[0], toshape[0], picpos=picposv)
    indh = _dimcomplete(pic.shape[1], toshape[1], picpos=picposh)

    # Fill the pre-allocated array :
    pictot[indv, indh] = pic

    return pictot


def _dimcomplete(N, dim, picpos='sup'):
    """Complete a picture over a single dimension.

    Args:
        N: integer
            Length of the picture across the diension.

        dim: integer
            Length of the final reshaped picture.

    Kargs:
        picpos: string, optional, (def: 'sup')
            Specify the alignement of the figure. Choose either
            'sup' (or 'left' / 'top'), 'inf' (or 'right' / 'bottom')
            or 'center'

    Returns:
        index: slice
            The slice where the picture start and finish.
    """
    if picpos in ['sup', 'left', 'top']:
        index = slice(0, N, 1)
    elif picpos in ['inf', 'right', 'bottom']:
        index = slice(dim-N, dim, 1)
    elif picpos is 'center':
        start = np.floor((dim / 2) - N / 2).astype(int)
        index = slice(start, start + N, 1)

    return index


def picconcat(pic, position):
    """Concatenate pictures acording to."""
    pass
