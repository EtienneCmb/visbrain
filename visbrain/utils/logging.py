"""Define visbrain logger.

See :
https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
"""
import logging
import sys

__all__ = ['set_log_level']


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
LOGGING_TYPES = dict(DEBUG=logging.DEBUG, INFO=logging.INFO,
                     WARNING=logging.WARNING, ERROR=logging.ERROR,
                     CRITICAL=logging.CRITICAL)
COLORS = {
    'DEBUG': GREEN,
    'INFO': WHITE,
    'WARNING': YELLOW,
    'ERROR': RED,
    'CRITICAL': RED,
}
FORMAT = {'compact': "$BOLD%(levelname)s | %(message)s",
          'spacy': "$BOLD%(levelname)-19s$RESET | %(message)s"
          }


def formatter_message(message, use_color=True):
    """Format the message."""
    return message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)


class _Formatter(logging.Formatter):
    """Formatter."""

    def __init__(self, format_type='compact'):
        logging.Formatter.__init__(self, FORMAT[format_type])

    def format(self, record):
        name = record.levelname
        levelname_color = COLOR_SEQ % (30 + COLORS[name]) + name + RESET_SEQ
        record.levelname = levelname_color
        return formatter_message(logging.Formatter.format(self, record))


class _StreamHandler(logging.StreamHandler):
    """Stream handler allowing matching and recording."""

    def __init__(self):
        logging.StreamHandler.__init__(self, sys.stderr)
        self.setFormatter(_lf)


logger = logging.getLogger('visbrain')
_lf = _Formatter()
_lh = _StreamHandler()  # needs _lf to exist
logger.addHandler(_lh)


def set_log_level(verbose=None):
    """Convenience function for setting the logging level.

    This function comes from the PySurfer package. See :
    https://github.com/nipy/PySurfer/blob/master/surfer/utils.py

    Parameters
    ----------
    verbose : bool, str, int, or None
        The verbosity of messages to print. If a str, it can be either DEBUG,
        INFO, WARNING, ERROR, or CRITICAL. Note that these are for
        convenience and are equivalent to passing in logging.DEBUG, etc.
        For bool, True is the same as 'INFO', False is the same as 'WARNING'.
        If None, the environment variable MNE_LOG_LEVEL is read, and if
        it doesn't exist, defaults to INFO.
    return_old_level : bool
        If True, return the old verbosity level.
    """
    # if verbose is None:
    #     verbose = "INFO"
    if isinstance(verbose, bool):
        verbose = 'INFO' if verbose else 'WARNING'
    if isinstance(verbose, str) and (verbose.upper() in LOGGING_TYPES):
        verbose = verbose.upper()
        verbose = LOGGING_TYPES[verbose]
        logger = logging.getLogger('visbrain')
        logger.setLevel(verbose)
