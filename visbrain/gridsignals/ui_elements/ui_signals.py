"""Interactions between user and Signal tab of QuickSettings."""
from ...utils import textline2color

__all__ = ('UiSignals')


class UiSignals(object):
    """Control axis and signal properties."""

    def __init__(self):
        """Init."""
        # Axis :
        self._axis_color.editingFinished.connect(self._fcn_axis_color)
        self._sig_title.textChanged.connect(self._fcn_axis_title)
        self._sig_title_fz.valueChanged.connect(self._fcn_axis_title_fz)
        self._sig_xlab.textChanged.connect(self._fcn_axis_xlab)
        self._sig_ylab.textChanged.connect(self._fcn_axis_ylab)
        self._sig_lab_fz.valueChanged.connect(self._fcn_axis_xlab_fz)
        self._sig_ticks_fz.valueChanged.connect(self._fcn_axis_ticks_fz)
        # Signal :
        self._sig_index.valueChanged.connect(self._fcn_set_signal)
        self._sig_form.currentIndexChanged.connect(self._fcn_set_signal)
        self._sig_color.editingFinished.connect(self._fcn_set_signal)
        self._sig_lw.valueChanged.connect(self._fcn_set_signal)
        self._sig_nbins.valueChanged.connect(self._fcn_set_signal)
        self._sig_size.valueChanged.connect(self._fcn_set_signal)
        self._sig_symbol.currentIndexChanged.connect(self._fcn_set_signal)
        # Amplitudes :
        self._sig_amp.clicked.connect(self._fcn_signal_amp)
        self._sig_amp_min.valueChanged.connect(self._fcn_signal_amp)
        self._sig_amp_max.valueChanged.connect(self._fcn_signal_amp)
        # Previous // Next :
        self._sig_prev.clicked.connect(self._fcn_prev_index)
        self._sig_next.clicked.connect(self._fcn_next_index)

    ###########################################################################
    #                                  AXIS
    ###########################################################################
    def _fcn_axis_color(self):
        """Set axis color."""
        col = textline2color(str(self._axis_color.text()))[1]
        self._signal_canvas.axis_color = col

    # ------------ TITLE ------------
    def _fcn_axis_title(self):
        """Set title of the axis."""
        self._signal_canvas.title = str(self._sig_title.text())

    def _fcn_axis_title_fz(self):
        """Set title font-size."""
        self._signal_canvas.title_font_size = self._sig_title_fz.value()

    # ------------ X-LABEL // Y-LABEL ------------
    def _fcn_axis_xlab(self):
        """Set x-label of the axis."""
        self._signal_canvas.xlabel = str(self._sig_xlab.text())

    def _fcn_axis_ylab(self):
        """Set y-label of the axis."""
        self._signal_canvas.ylabel = str(self._sig_ylab.text())

    def _fcn_axis_xlab_fz(self):
        """Set xlabel font-size."""
        self._signal_canvas.axis_font_size = self._sig_lab_fz.value()

    def _fcn_axis_ticks_fz(self):
        """Set tick size."""
        self._signal_canvas.tick_font_size = self._sig_ticks_fz.value()

    ###########################################################################
    #                                 SIGNAL
    ###########################################################################
    def _fcn_set_signal(self, *args, force=False):
        """Set signal."""
        # Index :
        index = int(self._sig_index.value())
        # Form and color :
        form_bck = self._signal.form
        form = str(self._sig_form.currentText())
        form_index = int(self._sig_form.currentIndex())
        self._PlottingForm.setCurrentIndex(form_index)
        color = textline2color(str(self._sig_color.text()))[0]
        # Enable amplitude control only for line // marker :
        self._sig_amp.setEnabled(form in ['line', 'marker'])
        # Line / marker / histogram :
        lw = float(self._sig_lw.value())
        nbins = int(self._sig_nbins.value())
        size = float(self._sig_size.value())
        symbol = str(self._sig_symbol.currentText())
        # Set data :
        self._signal.set_data(self._data, index, color, lw, nbins, symbol,
                              size, form)
        if force or (form != form_bck):
            self._sig_amp.setChecked(False)
            self.update_cameras(update='signal')
        # Set text :
        self._txt_shape.setText(str(self._signal))

    def _fcn_prev_index(self):
        """Go to previous index."""
        self._sig_index.setValue(int(self._sig_index.value()) - 1)

    def _fcn_next_index(self):
        """Go to next index."""
        self._sig_index.setValue(int(self._sig_index.value()) + 1)

    ###########################################################################
    #                            AMPLITUDE
    ###########################################################################
    def _fcn_signal_amp(self):
        """Control signal amplitude."""
        if self._sig_amp.isChecked():
            # Get rect :
            rect = list(self._signal.rect)
            # Get (min, max) amplitudes :
            minmax = (self._sig_amp_min.value(), self._sig_amp_max.value())
            rect[1] = .95 * minmax[0]
            rect[-1] = 1.05 * (minmax[1] - minmax[0])
            self.update_cameras(s_rect=rect, update='signal')
        else:
            self.update_cameras(update='signal')
