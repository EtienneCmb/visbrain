import numpy as np
from .color import color2vb


__all__ = ['slider2opacity', 'textline2color', 'uiSpinValue']


def slider2opacity(value, thmin=0.0, thmax=100.0, vmin=-5.0, vmax=105.0,
                   tomin=-1000.0, tomax=1000.0):
    """Convert a slider value to opacity

    Args:
        value: float
            The slider value

    Kargs:
        thmin: float (def: 0.0)
            Minimum threshold to consider

        thmax: float (def: 100.0)
            Maximum threshold to consider

        tomin: float (def: -1000.0)
            Set to tomin if value is under vmin

        tomax: float (def: 1000.0)
            Set to tomax if value is over vmax

    Return:
        color: array
            Array of RGBA colors
    """
    alpha = 0.0
    # Linear decrease :
    if value < thmin:
        alpha = value*tomin/vmin
    # Linear increase :
    elif value > thmax:
        alpha = value*tomax/vmax
    else:
        alpha = value/100
    return alpha


def textline2color(value):
    """Transform a Qt text line editor to color

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
        return 'w', (1,1,1,1)


def uiSpinValue(elements, values):
    """Set a list of value to a list of elements

    Args:
        elements: QtSpin
            List of qt spin elements

        values: list
            List of values per element   
    """
    if len(elements) != len(values):
        raise ValueError('List of Qt spins must have the same length as values')
    [k.setValue(i) for k, i in zip(elements, values)]