"""Interactions between user and Settings tab of QuickSettings."""
from ...utils import textline2color

__all__ = ('UiSettings')


class UiSettings(object):
    """Control axis and signal properties."""

    def __init__(self):
        """Init."""
        # Background color :
        self._set_bgcolor.editingFinished.connect(self._fcn_set_bgcolor)
        # Filtering :
        # Prepare data :
        self._sig_demean.clicked.connect(self._fcn_set_filtering)
        self._sig_detrend.clicked.connect(self._fcn_set_filtering)
        self._sig_filt.clicked.connect(self._fcn_set_filtering)
        self._sig_disp.currentIndexChanged.connect(self._fcn_set_filtering)
        self._sig_filter.currentIndexChanged.connect(self._fcn_set_filtering)
        self._sig_fmin.valueChanged.connect(self._fcn_set_filtering)
        self._sig_fmax.valueChanged.connect(self._fcn_set_filtering)
        self._sig_meth.currentIndexChanged.connect(self._fcn_set_filtering)
        self._sig_order.valueChanged.connect(self._fcn_set_filtering)

    def _fcn_set_bgcolor(self):
        """Change background color."""
        bgcolor = textline2color(str(self._set_bgcolor.text()))[1]
        self._grid_canvas.bgcolor = bgcolor
        self._signal_canvas.bgcolor = bgcolor

    def _fcn_set_filtering(self):
        """Filt the data."""
        # Grid :
        if hasattr(self, '_grid'):
            self._set_filtering_to_object(self._grid._prep)  # grid
            self._grid.set_data(self._data)
            self._grid.update()
            self.update_cameras(update='grid')
        # Signal :
        force = self._set_filtering_to_object(self._signal._prep)  # signal
        self._fcn_set_signal(force=force)

    def _set_filtering_to_object(self, prep):
        # Get demean // detrend // filtering :
        dem, det = self._sig_demean.isChecked(), self._sig_detrend.isChecked()
        filt = self._sig_filt.isChecked()
        # Get if camera nee update :
        filt_cam = (prep.demean == dem) or (prep.detrend == det) or (
            prep.filt == filt)
        # Set prepare data parameters :
        prep.demean, prep.detrend, prep.filt = dem, det, filt
        prep.dispas = str(self._sig_disp.currentText())
        prep.btype = str(self._sig_filter.currentText())
        prep.fstart = float(self._sig_fmin.value())
        prep.fend = float(self._sig_fmax.value())
        prep.filt_meth = str(self._sig_meth.currentText())
        prep.forder = int(self._sig_order.value())
        return filt_cam
