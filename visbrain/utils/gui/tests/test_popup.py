"""Test functions in popup.py."""
import sys
import types
from pathlib import Path

import numpy as np
import pytest

try:  # pragma: no cover - optional PyQt sip helper
    import sip
except ImportError:  # pragma: no cover - sip missing when PyQt absent
    sip = None

try:  # pragma: no cover - optional Qt bindings
    from visbrain.qt import QtWidgets, guard_qapp_lifecycle
except ImportError:  # pragma: no cover - Qt not installed
    QtWidgets = None
    guard_qapp_lifecycle = None


def _install_utils_stubs():
    """Install lightweight stubs to avoid heavy vispy imports during tests."""

    utils_key = "visbrain.utils"
    if utils_key not in sys.modules:
        utils_module = types.ModuleType(utils_key)
        utils_module.__path__ = [str(Path(__file__).resolve().parents[2])]
        sys.modules[utils_key] = utils_module

    guitools_key = "visbrain.utils.guitools"
    if guitools_key not in sys.modules:
        guitools_module = types.ModuleType(guitools_key)

        def textline2color(value):  # pragma: no cover - exercised indirectly
            cleaned = value.replace("'", "").strip()
            try:
                parts = [float(chunk.strip()) for chunk in cleaned.split(",")]
            except ValueError:
                parts = []
            if len(parts) < 3:
                parts = [1.0, 1.0, 1.0]
            if len(parts) == 3:
                parts.append(1.0)
            return cleaned, np.array([parts], dtype=float)

        guitools_module.textline2color = textline2color
        sys.modules[guitools_key] = guitools_module


_install_utils_stubs()

if guard_qapp_lifecycle is not None:  # pragma: no branch - skip when Qt missing
    guard_qapp_lifecycle()

if sip is not None:  # pragma: no cover - skip when sip missing
    try:
        sip.setdestroyonexit(False)
    except AttributeError:  # pragma: no cover - sip without setter
        pass

from visbrain.utils.gui.popup import HelpMenu, ScreenshotPopup, ShortcutPopup


pytestmark = [
    pytest.mark.skipif(QtWidgets is None, reason="Qt bindings are unavailable"),
    pytest.mark.gui,
]


class TestPopup:
    """Test functions in popup.py."""

    def test_shortcut_popup(self, qtbot):
        """Shortcut table is populated through set_shortcuts."""
        shortcuts = [("key1", "Action1"), ("key2", "Action2")]
        popup = ShortcutPopup()
        qtbot.addWidget(popup)

        popup.set_shortcuts(shortcuts)

        assert popup.table.rowCount() == len(shortcuts)
        for row, (key, description) in enumerate(shortcuts):
            assert popup.table.item(row, 0).text() == key
            assert popup.table.item(row, 1).text() == description

        popup.deleteLater()
        qtbot.wait(0)

    def test_screenshot_popup(self, qtbot):
        """Screenshot options toggle expected widgets and kwargs."""

        callback_triggered = []

        def dummy_callback():
            callback_triggered.append(True)

        popup = ScreenshotPopup(dummy_callback, canvas_names=["canvas1"])
        qtbot.addWidget(popup._ss)

        popup._ss.show()
        qtbot.wait(0)

        # Canvas selector visibility toggles with render selection
        assert popup._ssCanvasName.count() == 1
        assert not popup._ssCanvasW.isHidden()
        popup._ssSelect.setCurrentIndex(1)
        assert popup._ssCanvasW.isHidden()
        popup._ssSelect.setCurrentIndex(0)

        # Resolution switch toggles the configuration widgets
        popup._ssResolution.setCurrentIndex(1)
        assert not popup._ssCustomW.isVisible()
        assert popup._ssFactorW.isVisible()
        popup._ssResolution.setCurrentIndex(0)
        assert popup._ssCustomW.isVisible()
        assert not popup._ssFactorW.isVisible()

        # Background color checkbox enables the color input and is exported
        popup._ssBgcolorChk.setChecked(True)
        popup._fcn_enable_bgcolor()
        popup._ssBgcolor.setText("0.1, 0.2, 0.3")

        kwargs = popup.to_kwargs()
        assert kwargs["canvas"] == "canvas1"
        assert kwargs["print_size"] == (
            popup._ssWidth.value(),
            popup._ssHeight.value(),
        )
        assert np.allclose(kwargs["bgcolor"], np.array([[0.1, 0.2, 0.3, 1.0]]))

        popup._ssRun.click()
        assert callback_triggered

        popup._ss.deleteLater()
        qtbot.wait(0)

    def test_help_menu(self, qtbot):
        """Help menu exposes expected actions without extra applications."""

        class DummyWindow(QtWidgets.QMainWindow):
            def __init__(self):
                super().__init__()
                self._fcn_open_pdf_doc = types.MethodType(
                    HelpMenu._fcn_open_pdf_doc, self
                )
                HelpMenu.__init__(
                    self,
                    {"Overview": "https://example.org/help/overview"},
                    add_shortcuts=True,
                )

        window = DummyWindow()
        qtbot.addWidget(window)
        qtbot.addWidget(window._shpopup)

        help_action = next(
            action for action in window.menuBar().actions() if action.text() == "Help"
        )
        help_menu = help_action.menu()
        assert help_menu is not None

        shortcuts_action = next(
            action
            for action in help_menu.actions()
            if action.text().replace("&", "") == "Shortcuts"
        )
        assert isinstance(window._shpopup, ShortcutPopup)
        assert shortcuts_action.shortcut().toString() == "Ctrl+T"

        help_section_action = next(
            action for action in help_menu.actions() if action.menu() is not None
        )
        section_menu = help_section_action.menu()
        assert any(
            sub_action.text() == "&Overview" for sub_action in section_menu.actions()
        )

        pdf_action = help_menu.actions()[-1]
        assert pdf_action.text().startswith("&Download doc")

        window._shpopup.deleteLater()
        window.deleteLater()
        qtbot.wait(0)
