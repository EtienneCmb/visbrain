"""Main class for interactions with the menu."""
from ...io import write_fig_canvas

__all__ = ('UiMenu')


class UiMenu(object):
    """Interactions between the menu and the user."""

    def __init__(self):
        """Init."""
        self.menuScreenshot.triggered.connect(self._fcn_menu_screenshot)

    def _fcn_menu_screenshot(self):
        """Take a screenshot from the menu."""
        write_fig_canvas('test.png', self._view.canvas, autocrop=True)
