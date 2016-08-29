import numpy as np

__all__ = ['slider2opacity']

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