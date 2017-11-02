"""Test if dependencies are installed."""

__all__ = ('is_mne_installed', 'is_nibabel_installed', 'is_opengl_installed',
           'is_pandas_installed')


def is_mne_installed():
    """Test if MNE is installed."""
    try:
        import mne
        return True
    except:
        return False


def is_nibabel_installed():
    """Test if nibabel is installed."""
    try:
        import nibabel
        return True
    except:
        return False


def is_opengl_installed():
    """Test if OpenGL is installed."""
    try:
        import OpenGL.GL as GL
        return True
    except:
        return False


def is_pandas_installed():
    """Test if pandas is installed."""
    try:
        import pandas
        return True
    except:
        return False
