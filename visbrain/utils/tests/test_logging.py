"""Test functions in logging.py."""
import logging

from visbrain.utils.logging import set_log_level

logger = logging.getLogger('visbrain')


class TestLogging(object):
    """Test logging.py."""

    def test_set_log_level(self):
        """Test function set_log_level."""
        levels = [True, False, 'warning', 'error', 'critical', 'debug', 'info',
                  None]
        for k in levels:
            set_log_level(k)
            logger.debug('debug')
            logger.info('info')
            logger.warning('warnning')
            logger.error('error')
            logger.critical('critical')
