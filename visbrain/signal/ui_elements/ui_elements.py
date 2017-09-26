"""Initialize interactions between the user and the GUI."""
from .ui_menu import UiMenu, UiScreenshot
from .ui_signals import UiSignals
from .ui_annotations import UiAnnotations
from .ui_settings import UiSettings


class UiElements(UiMenu, UiScreenshot, UiSignals, UiAnnotations, UiSettings):
    """Gui interactions."""

    def __init__(self, **kwargs):
        """Init."""
        UiSignals.__init__(self)
        UiAnnotations.__init__(self)
        UiMenu.__init__(self)
        UiScreenshot.__init__(self)
        UiSettings.__init__(self)
