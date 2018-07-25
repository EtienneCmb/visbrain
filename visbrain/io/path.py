"""Set of functions for path definitions."""
import logging
import os
import sys

logger = logging.getLogger('visbrain')


__all__ = ['path_to_visbrain_data', 'get_files_in_folders', 'path_to_tmp',
           'clean_tmp', 'get_data_url_path']


def path_to_visbrain_data(file=None, folder=None):
    """Get the path to the visbrain_data folder.

    Parameters
    ----------
    folder : string | None
        Folder name.
    file : string | None
        File name. If None, only the path to the visbrain_data folder is
        returned.

    Returns
    -------
    path : string
        Path to the file or to the visbrain_data.
    """
    vb_path = os.path.join(os.path.expanduser('~'), 'visbrain_data')
    folder = '' if not isinstance(folder, str) else folder
    vb_path = os.path.join(vb_path, folder)
    if not os.path.exists(vb_path):
        os.makedirs(vb_path)
        logger.info("visbrain_data has been added to %s" % vb_path)
    file = '' if not isinstance(file, str) else file
    return os.path.join(vb_path, file)


def get_data_url_path():
    """Get the path to the data_url JSON file."""
    url_path = sys.modules[__name__].__file__.split('io')[0]
    return os.path.join(url_path, 'data_url.json')


def get_files_in_folders(*args, with_ext=False, with_path=False, file=None,
                         exclude=None, sort=True, unique=True):
    """Get all files in several folders.

    Parameters
    ----------
    args : string
        Path to folders.
    with_ext : bool | False
        Specify if returned files should contains extensions.
    with_path : bool | False
        Specify if returned files should contains full path to it.
    file : string | None
        Specify if a specific file name is needed.
    exclude : list | None
        List of patterns to exclude
    sort : bool | True
        Sort the resulting list of files.
    unique : bool | True
        Get a unique list of files.

    Returns
    -------
    files : list
        List of files in selected folders if no file is provided. If file is a
        string, return the path to it, None if the file doesn't exist.
    """
    # Search the file :
    files = []
    if isinstance(file, str):
        import glob
        for k in args:
            if os.path.exists(k):
                files += glob.glob(os.path.join(k, file))
        return files
    # Get the list of files :
    for k in args:
        if os.path.exists(k):
            if with_path:
                files += [os.path.join(k, i) for i in os.listdir(k)]
            else:
                files += os.listdir(k)
    # Keep only a selected file :
    if isinstance(file, str) and (file in files):
        files = [files[files.index(file)]]
    # Return either files with full path or only file name :
    if not with_ext:
        files = [os.path.splitext(k)[0] for k in files]
    # Patterns to exclude :
    if isinstance(exclude, (list, tuple)):
        from itertools import product
        files = [k for k, i in product(files, exclude) if i not in k]
    # Unique :
    if unique:
        files = list(set(files))
    # Sort list :
    if sort:
        files.sort()
    return files


def path_to_tmp(file=None, folder=None):
    """Get the path to the tmp folder."""
    tmp_path = os.path.join(path_to_visbrain_data(), 'tmp')
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    folder = '' if not isinstance(folder, str) else folder
    file = '' if not isinstance(file, str) else file
    tmp_path = os.path.join(tmp_path, folder)
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    return os.path.join(tmp_path, file)


def clean_tmp():
    """Clean the tmp folder."""
    tmp_path = os.path.join(path_to_visbrain_data(), 'tmp')
    if os.path.exists(tmp_path):
        import shutil
        shutil.rmtree(tmp_path)
