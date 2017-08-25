"""Main class for interactions with the menu."""

__all__ = ('UiMenu')


class UiMenu(object):
    """Interactions between the menu and the user."""

    def __init__(self):
        """Init."""
        self.menuScreenshot.triggered.connect(self._fcn_menu_screenshot)

    def _fcn_menu_screenshot(self):
        """Take a screenshot from the menu."""
        self.show_gui_screenshot()
