"""Test if dependencies are installed."""

__all__ = ('is_mne_installed', 'is_nibabel_installed', 'is_opengl_installed',
           'is_pandas_installed', 'is_faulthandler_installed',
           'is_lspopt_installed')


def is_mne_installed():
    """Test if MNE is installed."""
    try:
        import mne  # noqa
        return True
    except:
        return False


def is_nibabel_installed():
    """Test if nibabel is installed."""
    try:
        import nibabel  # noqa
        return True
    except:
        return False


def is_opengl_installed():
    """Test if OpenGL is installed."""
    try:
        import OpenGL.GL as GL  # noqa
        return True
    except:
        return False


def is_pandas_installed():
    """Test if pandas is installed."""
    try:
        import pandas  # noqa
        return True
    except:
        return False


def is_faulthandler_installed():
    """Test if faulthandler is installed."""
    try:
        import faulthandler  # noqa
        return True
    except:
        return False

def is_lspopt_installed():
    """Test if lspopt is installed."""
    try:
        import lspopt  # noqa
        return True
    except:
        return False
