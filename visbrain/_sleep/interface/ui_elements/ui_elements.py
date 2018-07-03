"""This script initialize all ui files."""

from .ui_settings import UiSettings
from .ui_panels import UiPanels
from .ui_info import UiInfo
from .ui_tools import UiTools
from .ui_scoring import UiScoring
from .ui_detection import UiDetection
from .ui_menu import UiMenu
from .ui_annotate import UiAnnotate
from .ui_screenshot import UiScreenshot
from ....config import PROFILER


class UiElements(UiSettings, UiPanels, UiInfo, UiTools, UiScoring,
                 UiDetection, UiAnnotate, UiMenu, UiScreenshot):
    """Inherit from the diffrent Ui files and initialize them."""

    def __init__(self):
        """Init."""
        for k in ['UiSettings', 'UiPanels', 'UiInfo', 'UiTools', 'UiScoring',
                  'UiDetection', 'UiAnnotate', 'UiMenu', 'UiScreenshot']:
            eval(k + '.__init__(self)')
            PROFILER("%s" % k, level=1)
