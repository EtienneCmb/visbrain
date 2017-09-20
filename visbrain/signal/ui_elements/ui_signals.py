"""Interactions between user and Signal tab of QuickSettings."""
from ...utils import textline2color, safely_set_spin

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
        self._sig_norm.currentIndexChanged.connect(self._fcn_display_apply_tf)
        self._sig_baseline.clicked.connect(self._fcn_display_apply_tf)
        self._sig_base_start.valueChanged.connect(self._fcn_display_apply_tf)
        self._sig_base_end.valueChanged.connect(self._fcn_display_apply_tf)
        self._sig_averaging.clicked.connect(self._fcn_display_apply_tf)
        self._sig_av_win.valueChanged.connect(self._fcn_display_apply_tf)
        self._sig_av_overlap.valueChanged.connect(self._fcn_display_apply_tf)
        self._sig_tf_apply.clicked.connect(self._fcn_set_signal)
        self._sig_tf_interp.currentIndexChanged.connect(self._fcn_set_tfinterp)
        # Amplitudes :
        self._sig_amp.clicked.connect(self._fcn_signal_amp)
        self._sig_amp_min.valueChanged.connect(self._fcn_signal_amp)
        self._sig_amp_max.valueChanged.connect(self._fcn_signal_amp)
        # Threshold :
        self._sig_th.clicked.connect(self._fcn_set_signal)
        self._sig_th_min.valueChanged.connect(self._fcn_set_signal)
        self._sig_th_max.valueChanged.connect(self._fcn_set_signal)
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
        self._signal_canvas.cbar.txtcolor = col

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
        # =================== FORM AND COLOR ===================
        form_bck = self._signal.form
        form = str(self._sig_form.currentText())
        form_index = int(self._sig_form.currentIndex())
        self._PlottingForm.setCurrentIndex(form_index)
        color = textline2color(str(self._sig_color.text()))[0]
        # Enable amplitude control only for line // marker :
        self._sig_amp.setEnabled(form in ['line', 'marker'])

        # =================== LINE / MARKER / HISTOGRAM ===================
        lw = float(self._sig_lw.value())
        nbins = int(self._sig_nbins.value())
        size = float(self._sig_size.value())
        symbol = str(self._sig_symbol.currentText())
        norm = int(self._sig_norm.currentIndex())
        is_baseline = self._sig_baseline.isChecked()
        _baseline = (int(self._sig_base_start.value()),
                     int(self._sig_base_end.value()))
        baseline = None if not is_baseline else _baseline
        is_averaging = self._sig_averaging.isChecked()
        window = None if not is_averaging else self._sig_av_win.value()
        overlap = float(self._sig_av_overlap.value())

        # =================== THRESHOLD ===================
        thm = (self._sig_th_min.value(), self._sig_th_max.value())
        th = thm if self._sig_th.isChecked() else None

        # =================== SET DATA // TEXT===================
        index = int(self._sig_index.value())
        self._signal.set_data(self._data, index, color, lw, nbins, symbol,
                              size, form, th, norm, window, overlap, baseline)
        self._txt_shape.setText(str(self._signal))

        # =================== CAMERA ===================
        if force or (form != form_bck):
            self._sig_amp.setChecked(False)
            self.update_cameras(update='signal')
        self._sig_tf_apply.setEnabled(False)

        # =================== RESIZE ===================
        main = self._signal_canvas.wc
        cbar = self._signal_canvas.wc_cbar
        title = self._signal_canvas._titleObj
        xaxis = self._signal_canvas.xaxis
        is_form = form in ['tf']
        if is_form:
            self._signal_canvas.grid.add_widget(cbar, row=1, col=2)
            self._signal_canvas.grid.resize_widget(main, 1, 1)
            self._signal_canvas.grid.resize_widget(xaxis, 1, 1)
            self._signal_canvas.grid.resize_widget(title, 1, 2)
        else:
            self._signal_canvas.grid.remove_widget(cbar)
            self._signal_canvas.grid.resize_widget(main, 1, 2)
            self._signal_canvas.grid.resize_widget(xaxis, 1, 2)
            self._signal_canvas.grid.resize_widget(title, 1, 3)

        # =================== CBAR ===================
        self._signal_canvas.wc_cbar.visible = is_form
        if form == 'tf':
            self._cbar_update(self._signal._tf)
        self._signal_canvas.update()

    def _fcn_display_apply_tf(self):
        """Display the apply TF button."""
        self._sig_tf_apply.setEnabled(True)

    def _fcn_set_tfinterp(self):
        """Set interpolation method."""
        self._signal._tf.interpolation = self._sig_tf_interp.currentText()

    def _safely_set_index(self, value, update_signal=False, force=False):
        """Set without trigger."""
        safely_set_spin(self._sig_index, value, [self._fcn_set_signal])
        if update_signal:
            self._fcn_set_signal(force=force)

    def _fcn_prev_index(self):
        """Go to previous index."""
        self._safely_set_index(int(self._sig_index.value()) - 1, True, True)

    def _fcn_next_index(self):
        """Go to next index."""
        self._safely_set_index(int(self._sig_index.value()) + 1, True, True)

    def _cbar_update(self, obj):
        """Update signal colorbar."""
        self._signal_canvas.cbar.clim = obj._clim
        self._signal_canvas.cbar.cblabel = obj._cblabel

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
            rect[1], rect[-1] = minmax[0], minmax[1] - minmax[0]
            self.update_cameras(s_rect=rect, update='signal')
        else:
            self.update_cameras(update='signal')
