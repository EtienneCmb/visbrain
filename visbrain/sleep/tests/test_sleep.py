"""Test Sleep module and related methods."""
import os

import numpy as np
from vispy.app.canvas import MouseEvent, KeyEvent
from vispy.util.keys import Key

from visbrain import Sleep
from visbrain.io import download_file, path_to_visbrain_data
from visbrain.tests._tests_visbrain import _TestVisbrain


# File to load :
sleep_file = path_to_visbrain_data('excerpt2.edf')
hypno_file = path_to_visbrain_data('Hypnogram_excerpt2.txt')

# Download sleep file :
if not os.path.isfile(sleep_file):
    download_file('sleep_edf.zip', unzip=True)
onset = np.array([100, 2000, 5000])

# Create Sleep application :
sp = Sleep(data=sleep_file, hypno=hypno_file, axis=True, annotations=onset)


class TestSleep(_TestVisbrain):
    """Test sleep.py."""

    ###########################################################################
    #                                TOOLS
    ###########################################################################
    def test_reference_switch(self):
        """Test function reference_switch."""
        for k in [2]:  # range(3)
            sp._ToolsRefMeth.setCurrentIndex(k)
            sp._fcn_ref_switch()
            sp._fcn_ref_apply()
        sp._fcn_ref_chan_ignore()

    def test_signal_processing(self):
        """Test function signal_processing."""
        sp._fcn_sig_processing()
        sp._SigMean.setChecked(True)
        sp._SigTrend.setChecked(True)
        sp._fcn_sig_processing()

    ###########################################################################
    #                                    GUI
    ###########################################################################
    def test_ui_detections(self):
        """Test method for detections."""
        sp._ToolDetectChan.setCurrentIndex(2)  # Select CZ channel
        for k in range(6):
            sp._ToolDetectType.setCurrentIndex(k)
            sp._fcn_apply_detection()

    def test_ui_annotations(self):
        """Test method for annotations."""
        # Add annotations :
        sp._fcn_annotate_add('', xlim=(10, 20), txt='Annotation1')
        sp._fcn_annotate_add('', xlim=(20, 30), txt='Annotation2')
        sp._fcn_annotate_add('', xlim=(5, 15), txt='Annotation3')
        # Remove annotation :
        sp._fcn_annotate_rm()
        # Go to :
        sp._fcn_annotate_goto()

    ###########################################################################
    #                                SAVE
    ###########################################################################
    def test_save_hyp_data(self):
        """Test saving hypnogram data."""
        from PyQt5 import QtWidgets
        yes = QtWidgets.QMessageBox.Yes
        no = QtWidgets.QMessageBox.No
        sp.saveHypData(filename=self.to_tmp_dir('hyp_data.txt'), reply=yes)
        sp.saveHypData(filename=self.to_tmp_dir('hyp_data.csv'), reply=yes)
        sp.saveHypData(filename=self.to_tmp_dir('hyp_data.xlsx'), reply=yes)
        sp.saveHypData(filename=self.to_tmp_dir('hyp_data.txt'), reply=no)
        sp.saveHypData(filename=self.to_tmp_dir('hyp_data.hyp'), reply=no)

    def test_save_hyp_figure(self):
        """Test saving hypnogram figure."""
        sp._save_hyp_fig(filename=self.to_tmp_dir('black_and_white.png'))
        sp._save_hyp_fig(filename=self.to_tmp_dir('black_and_white.png'),
                         ascolor=True)

    def test_save_info_table(self):
        """Test saving info table."""
        sp._save_info_table(filename=self.to_tmp_dir('info_table.txt'))
        sp._save_info_table(filename=self.to_tmp_dir('info_table.csv'))

    def test_save_scoring_table(self):
        """Test saving scoring table."""
        sp._save_scoring_table(filename=self.to_tmp_dir('scoring_table.txt'))
        sp._save_scoring_table(filename=self.to_tmp_dir('scoring_table.csv'))

    def test_save_all_detections(self):
        """Test saving all detections."""
        sp._save_all_detect(filename=self.to_tmp_dir('all_detections.npy'))

    def test_save_selected_dection(self):
        """Test saving selected dection."""
        sp._save_select_detect(filename=self.to_tmp_dir('selected_detect.txt'))
        sp._save_select_detect(filename=self.to_tmp_dir('selected_detect.csv'))

    def test_save_config(self):
        """Test saving config."""
        sp._save_config(filename=self.to_tmp_dir('config.txt'))

    def test_save_annotations(self):
        """Test saving annotations."""
        sp._save_annotation_table(filename=self.to_tmp_dir('annotations.txt'))
        sp._save_annotation_table(filename=self.to_tmp_dir('annotations.csv'))

    ###########################################################################
    #                                LOAD
    ###########################################################################
    def test_load_hypno(self):
        """Test loading hypno."""
        sp._load_hypno(filename=self.to_tmp_dir('hyp_data.txt'))
        sp._load_hypno(filename=self.to_tmp_dir('hyp_data.hyp'))

    def test_load_all_detections(self):
        """Test loading all detections."""
        sp._load_detect_all(filename=self.to_tmp_dir('all_detections.npy'))

    def test_load_selected_detection(self):
        """Test loading selected detection."""
        sp._load_detect_select(filename=self.to_tmp_dir("selected_detect_CZ-"
                                                        "Spindles.txt"))
        sp._load_detect_select(filename=self.to_tmp_dir("selected_detect_CZ-"
                                                        "Spindles.csv"))

    def test_load_annotations(self):
        """Test loading annotations."""
        # Txt :
        sp._load_annotation_table(filename=self.to_tmp_dir('annotations.txt'))
        # Csv :
        sp._load_annotation_table(filename=self.to_tmp_dir('annotations.csv'))
        # Onset only :
        sp._load_annotation_table(filename=np.array([10., 20., 3.]))
        # MNE annotations :
        from mne import Annotations
        onset = np.array([10., 20., 3.])
        durations = np.array([1., 1.5, 2.])
        annot = np.array(['Oki1', 'Okinawa', 'Okii'])
        annot = Annotations(onset, durations, annot)
        sp._load_annotation_table(filename=annot)

    def test_load_config(self):
        """Test load config."""
        sp._load_config(filename=self.to_tmp_dir('config.txt'))

    ###########################################################################
    #                             SHORTCUTS
    ###########################################################################

    @staticmethod
    def _key_pressed(canvas, ktype='key_press', key='', **kwargs):
        """Test VisPy KeyEvent."""
        k = KeyEvent(ktype, text=key, **kwargs)  # noqa
        eval('canvas.events.' + ktype + '(k)')

    @staticmethod
    def _mouse_event(canvas, etype='mouse_press', **kwargs):
        """Test a VisPy mouse event."""
        e = MouseEvent(etype, **kwargs)  # noqa
        eval('canvas.events.' + etype + '(e)')

    def test_key_window(self):
        """Test key for next // previous window."""
        self._key_pressed(sp._chanCanvas[0].canvas, key='n')
        self._key_pressed(sp._chanCanvas[0].canvas, key='b')

    def test_key_amplitude(self):
        """Test key for increase // decrease amplitude."""
        self._key_pressed(sp._chanCanvas[0].canvas, key='+')
        self._key_pressed(sp._chanCanvas[0].canvas, key='-')

    def test_key_staging(self):
        """Test key staging."""
        self._key_pressed(sp._chanCanvas[0].canvas, key='w')  # Wake
        self._key_pressed(sp._chanCanvas[0].canvas, key='r')  # REM
        self._key_pressed(sp._chanCanvas[0].canvas, key='1')  # N1
        self._key_pressed(sp._chanCanvas[0].canvas, key='2')  # N2
        self._key_pressed(sp._chanCanvas[0].canvas, key='3')  # N3
        self._key_pressed(sp._chanCanvas[0].canvas, key='a')  # Art

    def test_key_grid(self):
        """Test display hide grid."""
        self._key_pressed(sp._chanCanvas[0].canvas, key='g')  # On
        self._key_pressed(sp._chanCanvas[0].canvas, key='g')  # Off

    def test_key_magnify(self):
        """Test magnify."""
        self._key_pressed(sp._chanCanvas[0].canvas, key='m')  # On
        self._key_pressed(sp._chanCanvas[0].canvas, key='m')  # Off

    def test_mouse_move(self):
        """Test mouse move."""
        for k in [sp._chanCanvas[0], sp._specCanvas, sp._hypCanvas]:
            self._mouse_event(k.canvas, etype='mouse_move', pos=(50, 100))

    def test_mouse_press(self):
        """Test mouse press."""
        self._mouse_event(sp._chanCanvas[0].canvas, etype='mouse_press',
                          pos=(50, 100), modifiers=[Key('Control')], button=1)

    def test_mouse_double_click(self):
        """Test mouse double click."""
        for k in [sp._chanCanvas[0], sp._specCanvas, sp._hypCanvas]:
            self._mouse_event(k.canvas, etype='mouse_double_click',
                              pos=(50, 100))

    def test_mouse_release(self):
        """Test mouse release."""
        self._mouse_event(sp._chanCanvas[0].canvas, etype='mouse_release',
                          pos=(50, 100))
