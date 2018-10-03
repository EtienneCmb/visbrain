"""Manu interaction."""
import os
import numpy as np

from visbrain.utils import ScreenshotPopup, HelpMenu
from visbrain.io import (dialog_save, dialog_load, write_fig_pyqt,
                         write_fig_canvas, write_csv, write_txt)


class UiMenu(HelpMenu):
    """Interactions with the menu."""

    def __init__(self):
        """Init."""
        # Help menu :
        base = 'http://visbrain.org/signal.html'
        sections = {'Signal': base}
        HelpMenu.__init__(self, sections, True)
        # Save :
        self.saveAnnotations.triggered.connect(self._fcn_save_annotations)
        self.loadAnnotations.triggered.connect(self._fcn_load_annotations)
        # Display :
        self.actionQSP.triggered.connect(self._fcn_menu_disp_qsp)
        self.actionGrid.triggered.connect(self._fcn_menu_disp_grid)
        self.actionSignal.triggered.connect(self._fcn_menu_disp_signal)
        self.menuScreenshot.triggered.connect(self._fcn_menu_disp_screenshot)

    def _fcn_save_annotations(self, *args, filename=None):
        """Save annotations."""
        # Read Table
        row_count = self._annot_table.rowCount()
        time, amp, signal, text = [], [], [], []
        for row in range(row_count):
            time.append(self._annot_table.item(row, 0).text())
            amp.append(self._annot_table.item(row, 1).text())
            signal.append(self._annot_table.item(row, 2).text())
            text.append(self._annot_table.item(row, 3).text())
        # Get file name :
        if filename is None:
            filename = dialog_save(self, 'Save annotations', 'annotations',
                                   "CSV file (*.csv);;Text file (*.txt);;"
                                   "All files (*.*)")
        if filename:
            kw = {'delimiter': '_'}
            file, ext = os.path.splitext(filename)
            if ext.find('csv') + 1:
                write_csv(file + '.csv', zip(time, amp, signal, text), **kw)
            elif ext.find('txt') + 1:
                write_txt(file + '.txt', zip(time, amp, signal, text), **kw)

    def _fcn_load_annotations(self, *args, filename=None):
        """Load annotations."""
        # Get file name :
        if filename is None:
            filename = dialog_load(self, "Import annotations", '',
                                   "CSV file (*.csv);;Text file (*.txt);;"
                                   "All files (*.*)")
        # Clean annotations :
        self._annot_table.setRowCount(0)
        # Load the file :
        if isinstance(filename, str):  # 'file.txt'
            # Get starting/ending/annotation :
            time, amp, signal, text = np.genfromtxt(filename, delimiter='_',
                                                    dtype=str).T
            coords = np.c_[time, amp].astype(float)

        # Fill table :
        self._signal.clean_annotations()
        self._annot_table.setRowCount(0)
        # File the table :
        for k in range(len(signal)):
            self._annotate_event(signal[k], coords[k, :], text=text[k])

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
        filename = dialog_save(self, 'Screenshot', 'screenshot', "PNG (*.PNG)"
                               ";;TIFF (*.tiff);;JPG (*.jpg);;"
                               "All files (*.*)")
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
            write_fig_canvas(filename, c, widget=None, **kwargs)
