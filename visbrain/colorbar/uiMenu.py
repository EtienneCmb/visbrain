"""Main class for sleep menus managment."""

from ..io import dialogLoad, dialogSave, write_fig_canvas

__all__ = ['uiMenu']


class uiMenu(object):
    """Main class for sleep menus managment."""

    def __init__(self):
        """Init."""
        # __________ CONFIG __________
        self.actionSaveConfig.triggered.connect(self.saveConfig)
        self.actionLoadConfig.triggered.connect(self.loadConfig)
        self.actionScreenshot.triggered.connect(self._fcn_screenshot)

    def saveConfig(self):
        """Save colorbar config."""
        filename = dialogSave(self, 'Save config File', 'config',
                              "Text file (*.txt);;All files (*.*)")

        if filename:
            self.objs.save(filename)

    def loadConfig(self, *args, filename=None):
        """Load colorbar conf."""
        if filename is None:
            # Open dialog box :
            filename = dialogLoad(self, 'Load config File', 'config',
                                  "Text file (*.txt);;All files (*.*)")
            # Disconnect interactions :
            self._disconnect()

        if filename:
            # Load objects :
            self.objs.load(filename)
            # Update colorbar visual from loaded objects :
            self.objs.update_from_obj(self.cb)
            # re-build colorbar :
            self.cb._build(True, 'all')
            self._fcn_Name()
            # Update GUI :
            self._cb2GUI()
            self._initialize()
            # Re-connect interactions :
            self._connect()

    def _fcn_screenshot(self):
        """Colorbar screenshot."""
        filename = dialogSave(self, 'Save config File', 'config',
                              "PNG file (*.png);;JPG file (*.jpg);;TIFF file"
                              " (*.tiff);;All files (*.*)")
        write_fig_canvas(filename, self.cb._canvas, autocrop=True)
