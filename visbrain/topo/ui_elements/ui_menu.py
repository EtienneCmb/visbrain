"""Main class for interactions with the menu."""

from ...utils import HelpMenu


class UiMenu(HelpMenu):
    """Interactions between the menu and the user."""

    def __init__(self):
        """Init."""
        base = 'http://visbrain.org/topo.html'
        sections = {'Topo': base}
        HelpMenu.__init__(self, sections, False)
        self.menuScreenshot.triggered.connect(self._fcn_menu_screenshot)

    def _fcn_menu_screenshot(self):
        """Take a screenshot from the menu."""
        self.show_gui_screenshot()
