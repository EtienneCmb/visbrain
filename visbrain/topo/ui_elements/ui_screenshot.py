"""Screenshot window and related functions."""
from ...io import write_fig_pyqt, write_fig_canvas, dialog_save
from ...utils import ScreenshotPopup


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
            write_fig_canvas(filename, self._view.canvas, widget=self._grid,
                             **kwargs)
