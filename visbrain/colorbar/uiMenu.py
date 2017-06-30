"""Main class for sleep menus managment."""

from ..io import dialogLoad, dialogSave, write_fig_canvas

__all__ = ['uiMenu']


class uiMenu(object):
    """Main class for sleep menus managment."""

    def __init__(self):
        """Init."""
        # __________ CONFIG __________
        self.actionSaveConfig.triggered.connect(self.saveCbarConfig)
        self.actionLoadConfig.triggered.connect(self.loadCbarConfig)
        self.actionScreenshot.triggered.connect(self._fcn_screenshot)

    def saveCbarConfig(self):
        """Save colorbar config."""
        filename = dialogSave(self, 'Save config File', 'config',
                              "Text file (*.txt);;All files (*.*)")

        if filename:
            self.cbobjs.save(filename)

    def loadCbarConfig(self):
        """Load colorbar conf."""
        # Open dialog box :
        filename = dialogLoad(self, 'Load config File', 'config',
                              "Text file (*.txt);;All files (*.*)")

        if filename:
            self.cbobjs.load(filename)
            self._fcn_ChangeObj(clean=True)

    def _fcn_screenshot(self):
        """Colorbar screenshot."""
        filename = dialogSave(self, 'Save config File', 'config',
                              "PNG file (*.png);;JPG file (*.jpg);;TIFF file"
                              " (*.tiff);;All files (*.*)")
        if filename:
            write_fig_canvas(filename, self.cbviz._canvas, autocrop=True)
