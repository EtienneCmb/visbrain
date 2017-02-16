"""This script contains some other utility functions."""

__all__ = ['vis_args']


def vis_args(kw, prefix, ignore=[]):
    """Extract arguments that contain a prefix from a dictionary.

    Args:
        kw: dict
            The dictionary of arguments

        prefix: string
            The prefix to use (something like 'nd_', 'cb_'...)

    Returns:
        args: dict
            The dictionary which contain aguments starting with prefix.

        others: dict
            A dictionary with all other arguments.
    """
    # Create two dictionaries (for usefull args and others) :
    args, others = {}, {}
    l = len(prefix)
    #
    for k, v in zip(kw.keys(), kw.values()):
        entry = k[:l]
        if (entry == prefix) and (k not in ignore):
            args[k.replace(prefix, '')] = v
        else:
            others[k] = v
    return args, others
