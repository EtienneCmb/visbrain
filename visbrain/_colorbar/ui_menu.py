"""Main class for sleep menus managment."""

from ..io import write_fig_pyqt, write_fig_canvas, dialog_load, dialog_save
from ..utils import ScreenshotPopup, HelpMenu


class UiMenu(HelpMenu):
    """Main class for sleep menus managment."""

    def __init__(self):
        """Init."""
        base = 'http://visbrain.org/colorbar.html'
        sections = {'Colorbar': base}
        HelpMenu.__init__(self, sections, False)
        # __________ CONFIG __________
        self.menuCbarSaveConfig.triggered.connect(self._fcn_save_cbar_config)
        self.menuCbarLoadConfig.triggered.connect(self._fcn_load_cbar_config)
        self.menuCbarScreenshot.triggered.connect(self._fcn_cbar_screenshot)

    def _fcn_save_cbar_config(self, *args, filename=None):
        """Save colorbar config."""
        if filename is None:
            filename = dialog_save(self, 'Save config File', 'config',
                                   "Text file (*.txt);;All files (*.*)")

        if filename:
            self.cbqt.save(filename)

    def _fcn_load_cbar_config(self, *args, filename=None):
        """Load colorbar conf."""
        if filename is None:
            # Open dialog box :
            filename = dialog_load(self, 'Load config File', 'config',
                                   "Text file (*.txt);;All files (*.*)")

        if filename:
            self.cbqt.load(filename)
            self.cbqt._fcn_ChangeObj(clean=True)

    def _fcn_cbar_screenshot(self):
        """Colorbar screenshot."""
        self.show_gui_screenshot()


class UiScreenshot(object):
    """Initialize the screenshot GUI and functions to apply it."""

    def __init__(self):
        """Init."""
        canvas_names = ['main']
        self._ssGui = ScreenshotPopup(self._fcn_run_screenshot,
                                      canvas_names=canvas_names)

    def show_gui_screenshot(self):
        """Display the GUI screenhot."""
        self._ssGui.show()

    def _fcn_run_screenshot(self):
        """Run the screenshot."""
        # Get filename :
        filename = dialog_save(self, 'Screenshot', 'screenshot', "PNG (*.PNG)"
                               ";;TIFF (*.tiff);;JPG (*.jpg);;"
                               "All files (*.*)")
        # Get screenshot arguments :
        kwargs = self._ssGui.to_kwargs()

        if kwargs['entire']:  # Screenshot of the entire window
            self._ssGui._ss.close()
            write_fig_pyqt(self, filename)
        else:  # Screenshot of selected canvas
            # Remove unsed entries :
            del kwargs['entire'], kwargs['canvas']
            write_fig_canvas(filename, self.cbqt.cbviz._canvas,
                             widget=self.cbqt.cbviz._wc, **kwargs)
