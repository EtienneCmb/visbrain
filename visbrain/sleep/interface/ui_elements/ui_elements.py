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


class UiElements(UiSettings, UiPanels, UiInfo, UiTools, UiScoring,
                 UiDetection, UiAnnotate, UiMenu, UiScreenshot):
    """Inherit from the diffrent Ui files and initialize them."""

    def __init__(self):
        """Init."""
        UiSettings.__init__(self)
        UiPanels.__init__(self)
        UiInfo.__init__(self)
        UiTools.__init__(self)
        UiScoring.__init__(self)
        UiDetection.__init__(self)
        UiAnnotate.__init__(self)
        UiMenu.__init__(self)
        UiScreenshot.__init__(self)
