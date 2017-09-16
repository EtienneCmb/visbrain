"""Initialize interactions between the user and the GUI."""
from .ui_menu import UiMenu, UiScreenshot
from .ui_grid import UiGrid
from .ui_signals import UiSignals
from .ui_annotations import UiAnnotations
from .ui_settings import UiSettings


__all__ = ('UiElements')


class UiElements(UiMenu, UiScreenshot, UiGrid, UiSignals, UiAnnotations,
                 UiSettings):
    """Gui interactions."""

    def __init__(self, **kwargs):
        """Init."""
        UiGrid.__init__(self)
        UiSignals.__init__(self)
        UiAnnotations.__init__(self)
        UiMenu.__init__(self)
        UiScreenshot.__init__(self)
        UiSettings.__init__(self)
