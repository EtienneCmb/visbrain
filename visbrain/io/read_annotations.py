"""Read annotations."""
import numpy as np
from .dependencies import is_mne_installed

__all__ = ['annotations_to_array', 'merge_annotations']


def annotations_to_array(annotations, default_txt='enter annotations'):
    """Convert annotations to array.

    Parameters
    ----------
    annotations : string, array_like, mne.io.annotations.Annotations
        Annotations to use. Should either be a string for a path to an
        annotation file, an Annotation instance from MNE or a 1-D or 3-D array
        of annotations (e.g. start, end, text).
    default_txt : string | 'enter annotations'
        Default text to use if no text is given.

    Returns
    -------
    start : array_like
        First array of float.
    end : array_like
        Second array of float.
    text : array_like
        Array of text.
    """
    if annotations is None:
        start = end = text = np.array([])
    elif isinstance(annotations, str):  # 'file.txt'
        # Get starting/ending/annotation :
        start, end, text = np.genfromtxt(annotations, delimiter=',',
                                         dtype=str, encoding='utf-8').T
    elif isinstance(annotations, (np.ndarray, list)):  # array of annotations
        annotations = np.asarray(annotations)
        if (annotations.ndim == 1):
            start = end = annotations
            text = np.array(['enter annotations'] * len(start))
        elif (annotations.ndim == 2) and (annotations.shape[1] == 3):
            start, end, text = annotations.T
            start = start.astype(float)
    elif is_mne_installed():  # MNE annotations
        import mne
        if isinstance(annotations, mne.annotations.Annotations):
            start = annotations.onset
            end = annotations.onset + annotations.duration
            text = annotations.description
    else:
        raise ValueError("Annotation's type not supported.")

    return start.astype(float), end.astype(float), text


def merge_annotations(*args):
    """Merge several annotations together.

    Parameters
    ----------
    args : string, array_like, mne.io.annotations.Annotations
        Annotation file / array / MNE instance.

    Returns
    -------
    start : array_like
        First array of float.
    end : array_like
        Second array of float.
    text : array_like
        Array of text.
    """
    start = end = text = np.array([])
    for k in args:
        # Convert annotations :
        start_t, end_t, text_t = annotations_to_array(k)
        # Extend start, end and text :
        start = np.append(start, start_t)
        end = np.append(end, end_t)
        text = np.append(text, text_t)
    return start, end, text
