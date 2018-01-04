"""Test functions in popup.py."""
import pytest
from PyQt5 import QtWidgets

from visbrain.utils.gui.popup import (ShortcutPopup, ScreenshotPopup, HelpMenu)


class TestPopup(object):
    """Test functions in popup.py."""

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_shortcut_popup(self):
        """Test function ShortcutPopup."""
        sh = [('key1', 'Action1'), ('key2', 'Action2')]
        app = QtWidgets.QApplication([])  # noqa
        pop = ShortcutPopup()
        pop.set_shortcuts(sh)
        # app.quit()

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_screenshot_popup(self):
        """Test function ScreenshotPopup."""
        def fcn():
            pass
        app = QtWidgets.QApplication([])  # noqa
        sc = ScreenshotPopup(fcn)
        sc._fcn_select_render()
        sc._fcn_resolution()
        sc.to_kwargs()
        sc._fcn_enable_bgcolor()
        # app.quit()

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_help_menu(self):
        """Test function HelpMenu."""
        HelpMenu()
