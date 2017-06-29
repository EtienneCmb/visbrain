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
        print(self.cbobjs.to_dict())

    def loadConfig(self):
        """Load colorbar conf."""
        pass

    def _fcn_screenshot(self):
        """Colorbar screenshot."""
        filename = dialogSave(self, 'Save config File', 'config',
                              "PNG file (*.png);;JPG file (*.jpg);;TIFF file"
                              " (*.tiff);;All files (*.*)")
        write_fig_canvas(filename, self.cb._canvas, autocrop=True)
