"""Screenshot window and related functions."""
from visbrain.io import write_fig_pyqt, write_fig_canvas, dialog_save
from visbrain.utils import ScreenshotPopup


class UiScreenshot(object):
    """Initialize the screenshot GUI and functions to apply it."""

    def __init__(self):
        """Init."""
        # Get the list of canvas channel names :
        cn = self._channels + ['spectrogram', 'hypnogram', 'topoplot']
        # Create the screenshot GUI :
        self._ssGui = ScreenshotPopup(self._fcn_run_screenshot,
                                      canvas_names=cn)
        # In Sleep module, disable background and transparency :
        self._ssGui._ssBgcolor.hide()
        self._ssGui._ssBgcolorChk.hide()
        self._ssGui._ssTransp.hide()

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
            # Get canvas name :
            name = kwargs['canvas']
            # Remove unsed entries :
            del kwargs['entire'], kwargs['canvas']
            if name == 'spectrogram':
                # Force the spectrogram to be displayed :
                self.menuDispSpec.setChecked(True)
                self._disptog_spec()
                # Get canvas
                canvas = self._specCanvas.canvas
            elif name == 'hypnogram':
                # Force the spectrogram to be displayed :
                self.menuDispHypno.setChecked(True)
                self._disptog_hyp()
                # Get canvas
                canvas = self._hypCanvas.canvas
            elif name == 'topoplot':
                # Force the spectrogram to be displayed :
                self.menuDispTopo.setChecked(True)
                self._disptog_topo()
                # Get canvas :
                canvas = self._topoCanvas.canvas
            else:
                # Get the index of this channel :
                kc = self._channels.index(name)
                # Force the channel to be displayed :
                self._chanChecks[kc].setChecked(True)
                self._fcn_chan_viz()
                canvas = self._chanCanvas[kc].canvas
            # Finally, render the canvas :
            write_fig_canvas(filename, canvas=canvas, **kwargs)
