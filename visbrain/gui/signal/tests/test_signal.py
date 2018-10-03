"""Test Signal module and related methods."""
from vispy.app.canvas import MouseEvent, KeyEvent

from visbrain.gui import Signal
from visbrain.utils import generate_eeg
from visbrain.tests._tests_visbrain import _TestVisbrain

# Generate random EEG dataset :
sf = 512.
data, time = generate_eeg(sf=sf, n_channels=3, n_trials=2)

# ---------------- Kwargs  ----------------
kwargs = {'xlabel': 'My xlabel', 'ylabel': 'My ylabel', 'title': 'My title',
          'display_grid': True, 'color': 'darkgray', 'symbol': 'x',
          'title_font_size': 20, 'axis_font_size': 18, 'tick_font_size': 8,
          'axis_color': 'blue', 'bgcolor': 'white', 'enable_grid': True,
          'display_signal': True, 'form': 'psd'}

# ---------------- Application  ----------------
sig = Signal(data, sf=sf, axis=-1, time=time)


class TestSignal(_TestVisbrain):
    """Test signal.py."""

    ###########################################################################
    #                                 LABELS
    ###########################################################################
    def test_xlabel(self):
        """Test setting xlabel."""
        # Text :
        sig._sig_xlab.setText('New x label')
        sig._fcn_axis_xlab()
        # Size :
        sig._sig_lab_fz.setValue(24.)
        sig._fcn_axis_lab_fz()

    def test_ylabel(self):
        """Test setting ylabel."""
        # Text :
        sig._sig_ylab.setText('New y label')
        sig._fcn_axis_ylab()
        # Size :
        sig._sig_lab_fz.setValue(27.)
        sig._fcn_axis_lab_fz()

    def test_title(self):
        """Test setting title."""
        # Text :
        sig._sig_title.setText('New title')
        sig._fcn_axis_title()
        # Font size :
        sig._sig_title_fz.setValue(23.)
        sig._fcn_axis_title_fz()

    def test_axis_color(self):
        """Test setting axis color."""
        sig._axis_color.setText('green')
        sig._fcn_axis_color()

    ###########################################################################
    #                                 LINE
    ###########################################################################
    def test_line_form(self):
        """Test setting line."""
        sig._sig_form.setCurrentIndex(0)
        sig._fcn_set_signal(force=True)

    def test_line_color(self):
        """Test setting line color."""
        sig._sig_color.setText('#ab4642')
        sig._fcn_set_signal()

    def test_line_width(self):
        """Test setting line width."""
        sig._sig_lw.setValue(1.5)
        sig._fcn_set_signal()

    def test_line_threshold(self):
        """Test setting line threshold."""
        sig._sig_th.setChecked(True)
        sig._sig_th_min.setValue(-.5)
        sig._sig_th_max.setValue(-.5)
        sig._fcn_set_signal()

    def test_line_amplitude(self):
        """Test setting line amplitude."""
        sig._sig_amp.setChecked(True)
        sig._sig_amp_min.setValue(-.5)
        sig._sig_amp_max.setValue(-.5)
        sig._fcn_set_signal()

    ###########################################################################
    #                                 MARKERS
    ###########################################################################
    def test_marker_form(self):
        """Test setting marker."""
        sig._sig_form.setCurrentIndex(1)
        sig._fcn_set_signal(force=True)

    def test_marker_size(self):
        """Test setting marker size."""
        sig._sig_size.setValue(15.)
        sig._fcn_set_signal()

    def test_marker_color(self):
        """Test setting marker color."""
        sig._sig_color.setText('green')
        sig._fcn_set_signal()

    def test_marker_symbol(self):
        """Test setting marker symbol."""
        sig._sig_symbol.setCurrentIndex(7)
        sig._fcn_set_signal()

    ###########################################################################
    #                                 HIST
    ###########################################################################
    def test_hist(self):
        """Test setting hist."""
        sig._sig_form.setCurrentIndex(2)
        sig._fcn_set_signal(force=True)

    def test_hist_color(self):
        """Test function hist_color."""
        sig._sig_color.setText('(.1, .1, .1)')
        sig._fcn_set_signal()

    def test_hist_nbins(self):
        """Test function hist_nbins."""
        sig._sig_nbins.setValue(124)
        sig._fcn_set_signal()

    ###########################################################################
    #                                 TF
    ###########################################################################
    def test_tf(self):
        """Test setting tf."""
        sig._sig_form.setCurrentIndex(3)
        sig._fcn_set_signal(force=True)

    def test_tf_normalization(self):
        """Test setting tf normalization."""
        for k in range(sig._sig_norm.count()):
            sig._sig_norm.setCurrentIndex(k)
            sig._fcn_set_signal()

    def test_tf_interpolation(self):
        """Test setting tf interpolation."""
        for k in range(sig._sig_tf_interp.count()):
            sig._sig_tf_interp.setCurrentIndex(k)
            sig._fcn_set_tfinterp()

    def test_tf_cmap(self):
        """Test setting tf cmap."""
        # Set one random colormap :
        sig._sig_tf_rev.setChecked(True)
        sig._sig_tf_cmap.setCurrentIndex(11)
        sig._fcn_set_signal()

    def test_tf_baseline(self):
        """Test setting tf baseline."""
        sig._sig_baseline.setChecked(True)
        sig._sig_base_start.setValue(0)
        sig._sig_base_end.setValue(10)
        sig._fcn_set_signal()

    def test_tf_averaging(self):
        """Test setting tf averaging."""
        sig._sig_averaging.setChecked(True)
        sig._sig_av_win.setValue(10)
        sig._sig_av_overlap.setValue(.5)
        sig._fcn_set_signal()

    def test_tf_clim(self):
        """Test setting tf clim."""
        sig._sig_tf_clim.setChecked(True)
        sig._sig_climin.setValue(-1.)
        sig._sig_climax.setValue(1.)
        sig._fcn_set_signal()

    def test_tf_apply(self):
        """Test setting tf apply."""
        sig._fcn_disp_apply_tf()

    ###########################################################################
    #                                 PSD
    ###########################################################################
    def test_psd(self):
        """Test setting psd."""
        sig._sig_form.setCurrentIndex(4)
        sig._fcn_set_signal(force=True)

    def test_psd_nperseg(self):
        """Test setting psd nperseg."""
        sig._sig_nperseg.setValue(500)
        sig._fcn_set_signal()

    def test_psd_noverlap(self):
        """Test setting psd noverlap."""
        sig._sig_noverlap.setValue(10)
        sig._fcn_set_signal()

    ###########################################################################
    #                                 TOOLS
    ###########################################################################
    def test_bgcolor(self):
        """Test setting bgcolor."""
        sig._set_bgcolor.setText('black')
        sig._fcn_set_bgcolor()

    def test_filtering(self):
        """Test setting filtering."""
        sig._sig_filt.setChecked(True)
        sig._fcn_display_apply()
        sig._fcn_set_filtering()

    ###########################################################################
    #                              ANNOTATIONS
    ###########################################################################
    def test_add_annotations(self):
        """Test add annotations."""
        sig._annotate_event('(1, 0, :)', (10.5, 3.), 'First annotation')
        sig._annotate_event('(0, 1, :)', (14.1, -1.), 'Second annotation')
        sig._annotate_event('(2, 0, :)', (2.1, -2.5), 'Third annotation')
        sig._annotate_event('(2, 1, :)', (12.3, -0.8), 'Fourth annotation')
        sig._fcn_annot_goto()
        sig._fcn_text_edited()

    def test_save_annotations(self):
        """Test save annotations."""
        sig._fcn_save_annotations(filename=self.to_tmp_dir('annot.csv'))
        sig._fcn_save_annotations(filename=self.to_tmp_dir('annot.txt'))

    def test_load_annotations(self):
        """Test load annotations."""
        sig._fcn_load_annotations(filename=self.to_tmp_dir('annot.csv'))
        sig._fcn_load_annotations(filename=self.to_tmp_dir('annot.txt'))

    ###########################################################################
    #                              DISPLAY
    ###########################################################################
    def test_display_quicksettings(self):
        """Test display quicksettings."""
        sig._fcn_menu_disp_qsp()

    def test_display_signal(self):
        """Test display signal."""
        sig._fcn_menu_disp_signal()

    def test_display_grid(self):
        """Test display grid."""
        sig._fcn_menu_disp_grid()

    ###########################################################################
    #                              MOUSE EVENT
    ###########################################################################
    def test_key_next_signal(self):
        """Test function next_signal."""
        k = KeyEvent('key_press', text='n')
        sig._signal_canvas.canvas.events.key_press(k)

    def test_key_previous_signal(self):
        """Test function previous_signal."""
        k = KeyEvent('key_press', text='b')
        sig._signal_canvas.canvas.events.key_press(k)

    def test_mouse_double_click_signal(self):
        """Test function mouse_double_click for signal."""
        sig._sig_form.setCurrentIndex(0)
        sig._fcn_set_signal(force=True)
        ev = MouseEvent('mouse_double_click', pos=(200, 300))
        sig._signal_canvas.canvas.events.mouse_double_click(ev)

    def test_mouse_double_click_grid(self):
        """Test function mouse_double_click for grid."""
        ev = MouseEvent('mouse_double_click', pos=(200, 300))
        sig._grid_canvas.canvas.events.mouse_double_click(ev)
