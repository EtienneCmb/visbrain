"""Manu interaction."""
from ...utils import ScreenshotPopup, HelpMenu
from ...io import dialogSave, write_fig_pyqt, write_fig_canvas

__all__ = ('UiMenu', 'UiScreenshot')


class UiMenu(HelpMenu):
    """Interactions with the menu."""

    def __init__(self):
        """Init."""
        # Help menu :
        base = 'http://visbrain.org/signal.html'
        sections = {'Signal': base}
        HelpMenu.__init__(self, sections, True)
        # # Display :
        self.actionQSP.triggered.connect(self._fcn_menu_disp_qsp)
        self.actionGrid.triggered.connect(self._fcn_menu_disp_grid)
        self.actionSignal.triggered.connect(self._fcn_menu_disp_signal)
        self.menuScreenshot.triggered.connect(self._fcn_menu_disp_screenshot)

    def _fcn_menu_disp_qsp(self):
        """Display quick settings panel."""
        self.q_widget.setVisible(self.actionQSP.isChecked())

    def _fcn_menu_disp_grid(self):
        """Display grid layout."""
        self._GridWidget.setVisible(self.actionGrid.isChecked())

    def _fcn_menu_disp_signal(self):
        """Display signal layout."""
        self._SignalWidget.setVisible(self.actionSignal.isChecked())

    def _fcn_menu_disp_screenshot(self):
        """Display screenshot window."""
        self.show_gui_screenshot()


class UiScreenshot(object):
    """Initialize the screenshot GUI and functions to apply it."""

    def __init__(self):
        """Init."""
        canvas_names = ['Grid', 'Signal']
        self._ssGui = ScreenshotPopup(self._fcn_run_screenshot,
                                      canvas_names=canvas_names)

    def show_gui_screenshot(self):
        """Display the GUI screenhot."""
        self._ssGui.show()

    def _fcn_run_screenshot(self):
        """Run the screenshot."""
        # Get filename :
        filename = dialogSave(self, 'Screenshot', 'screenshot', "PNG (*.PNG);;"
                              "TIFF (*.tiff);;JPG (*.jpg);;""All files (*.*)")
        # Get screenshot arguments :
        kwargs = self._ssGui.to_kwargs()

        if kwargs['entire']:  # Screenshot of the entire window
            self._ssGui._ss.close()
            write_fig_pyqt(self, filename)
        elif kwargs['canvas'] in ['Grid', 'Signal']:  # Selected canvas
            # Remove unsed entries :
            if kwargs['canvas'] == 'Grid':
                c = self._grid_canvas.canvas
            elif kwargs['canvas'] == 'Signal':
                c = self._signal_canvas.canvas
            del kwargs['entire'], kwargs['canvas']
            w = None
            write_fig_canvas(filename, c, widget=w, **kwargs)
