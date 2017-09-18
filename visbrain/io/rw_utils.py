"""Utility functions for saving/loading files.

- get_file_ext : Get the filename and extension
- safety_save : If a file exist, avoid arasing it when saving.
"""
import os

__all__ = ('get_file_ext', 'safety_save')


def get_file_ext(path):
    """Get the filename and extension.

    Parameters
    ----------
    path : string
        Path to the file.

    Returns
    -------
    file : string
        Name of the file
    ext : string
        Extension of the file.
    """
    # Test if the path exist and if it is a file (not a directory):
    if not os.path.isfile(path):
        # If it is a directory, check if it is a mff directory
        if path[-3:].lower() != "mff":
            raise ValueError("The provided path (" + path + ") is not valid.")
    # Find file extension :
    file, ext = os.path.splitext(path)
    # Be sure to be in lowercase :
    ext = ext.lower()
    return file, ext


def safety_save(path, limit=100):
    """If a file exist, avoid erasing it when saving.

    Parameters
    ----------
    path : string
        Path to the file.
    limit : int | 100
        Limit for the filename occurence.

    Returns
    -------
    name : string
        Unique filename.
    """
    k = 1
    while os.path.isfile(path) and (k < limit):
        fname, fext = os.path.splitext(path)
        if fname.find('(') + 1:
            path = fname[0:fname.find('(') + 1] + str(k) + ')' + fext
        else:
            path = fname + '(' + str(k) + ')' + fext
        k += 1
    return path
