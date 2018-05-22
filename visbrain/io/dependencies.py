"""Test if dependencies are installed."""

__all__ = ('is_mne_installed', 'is_nibabel_installed', 'is_opengl_installed',
           'is_pandas_installed', 'is_lspopt_installed',
           'is_tensorpac_installed', 'is_xlrd_installed')


def is_mne_installed(raise_error=False):
    """Test if MNE is installed."""
    try:
        import mne  # noqa
        is_installed = True
    except:
        is_installed = False
    # Raise error (if needed) :
    if raise_error and not is_installed:
        raise IOError("mne-python not installed. See https://github.com/mne-"
                      "tools/mne-python for installation instructions.")
    return is_installed


def is_nibabel_installed(raise_error=False):
    """Test if nibabel is installed."""
    try:
        import nibabel  # noqa
        is_installed = True
    except:
        is_installed = False
    # Raise error (if needed) :
    if raise_error and not is_installed:
        raise IOError("nibabel not installed. See https://github.com/nipy/"
                      "nibabel for installation instructions.")
    return is_installed


def is_opengl_installed(raise_error=False):
    """Test if OpenGL is installed."""
    try:
        import OpenGL.GL as GL  # noqa
        is_installed = True
    except:
        is_installed = False
    # Raise error (if needed) :
    if raise_error and not is_installed:
        raise IOError("OpenGL not installed. See http://vispy.org/installation"
                      ".html#backend-requirements for installation "
                      "instructions.")
    return is_installed


def is_pandas_installed(raise_error=False):
    """Test if pandas is installed."""
    try:
        import pandas  # noqa
        is_installed = True
    except:
        is_installed = False
    # Raise error (if needed) :
    if raise_error and not is_installed:
        raise IOError("pandas not installed. See https://pandas.pydata.org/#"
                      "best-way-to-install for installation instructions.")
    return is_installed


def is_lspopt_installed(raise_error=False):
    """Test if lspopt is installed."""
    try:
        import lspopt  # noqa
        is_installed = True
    except:
        is_installed = False
    # Raise error (if needed) :
    if raise_error and not is_installed:
        raise IOError("lspopt not installed. See https://github.com/hbldh/"
                      "lspopt#installation for installation instructions.")
    return is_installed


def is_tensorpac_installed(raise_error=False):
    """Test if tensorpac is installed."""
    try:
        import tensorpac  # noqa
        is_installed = True
    except:
        is_installed = False
    # Raise error (if needed) :
    if raise_error and not is_installed:
        raise IOError("tensorpac not installed. See https://github.com/Etienne"
                      "Cmb/tensorpac#installation for installation "
                      "instructions.")
    return is_installed


def is_xlrd_installed(raise_error=False):
    """Test if xlrd is installed."""
    try:
        import xlrd  # noqa
        is_installed = True
    except:
        is_installed = False
    # Raise error (if needed) :
    if raise_error and not is_installed:
        raise IOError("xlrd not installed. In a terminal, run : pip install "
                      "xlrd")
    return is_installed
