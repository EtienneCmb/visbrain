"""Main class for sleep menus managment."""

from ..io import dialogLoad, dialogSave, write_fig_canvas

__all__ = ['uiMenu']


class uiMenu(object):
    """Main class for sleep menus managment."""

    def __init__(self):
        """Init."""
        # __________ CONFIG __________
        self.menuCbarSaveConfig.triggered.connect(self._fcn_saveCbarConfig)
        self.menuCbarLoadConfig.triggered.connect(self._fcn_loadCbarConfig)
        self.menuCbarScreenshot.triggered.connect(self._fcn_CbarScreenshot)

    def _fcn_saveCbarConfig(self):
        """Save colorbar config."""
        filename = dialogSave(self, 'Save config File', 'config',
                              "Text file (*.txt);;All files (*.*)")

        if filename:
            self.cbqt.save(filename)

    def _fcn_loadCbarConfig(self):
        """Load colorbar conf."""
        # Open dialog box :
        filename = dialogLoad(self, 'Load config File', 'config',
                              "Text file (*.txt);;All files (*.*)")

        if filename:
            self.cbqt.load(filename)
            self.cbqt._fcn_ChangeObj(clean=True)

    def _fcn_CbarScreenshot(self):
        """Colorbar screenshot."""
        filename = dialogSave(self, 'Save config File', 'config',
                              "PNG file (*.png);;JPG file (*.jpg);;TIFF file"
                              " (*.tiff);;All files (*.*)")
        if filename:
            write_fig_canvas(filename, self.cbqt.cbviz._canvas, autocrop=True)
