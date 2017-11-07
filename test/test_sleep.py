"""Test Sleep module and related methods."""
import os
import shutil

import numpy as np
from vispy.app.canvas import MouseEvent, KeyEvent
from vispy.util.keys import Key

from visbrain import Sleep
from visbrain.io import download_file

# Create a tmp/ directory :
dir_path = os.path.dirname(os.path.realpath(__file__))
path_to_tmp = os.path.join(*(dir_path, 'tmp'))

# Create a random dataset :
download_file('sleep_edf.zip', to_path=path_to_tmp, unzip=True)
onset = np.array([100, 2000, 5000])


def path_to_edf(name):
    """Get path to the edf file."""
    return os.path.join(path_to_tmp, name)

# Create Sleep application :
sp = Sleep(data=path_to_edf('excerpt2.edf'),
           hypno=path_to_edf('Hypnogram_excerpt2.txt'), axis=True, hedit=True,
           annotations=onset)


class TestSleep(object):
    """Test sleep.py."""

    ###########################################################################
    #                                 SETTINGS
    ###########################################################################
    def test_create_tmp_folder(self):
        """Create tmp folder."""
        if not os.path.exists(path_to_tmp):
            os.makedirs(path_to_tmp)

    @staticmethod
    def _path_to_tmp(name):
        return os.path.join(*(path_to_tmp, name))

    ###########################################################################
    #                                    GUI
    ###########################################################################
    def test_ui_detections(self):
        """Test method for detections."""
        sp._ToolDetectChan.setCurrentIndex(2)  # Select CZ channel
        for k in range(6):
            sp._ToolDetectType.setCurrentIndex(k)
            sp._fcn_applyDetection()

    def test_ui_annotations(self):
        """Test method for annotations."""
        # Add annotations :
        sp._fcn_annotateAdd('', xlim=(10, 20), txt='Annotation1')
        sp._fcn_annotateAdd('', xlim=(20, 30), txt='Annotation2')
        sp._fcn_annotateAdd('', xlim=(5, 15), txt='Annotation3')
        # Remove annotation :
        sp._fcn_annotateRm()
        # Go to :
        sp._fcn_annotateGoto()

    ###########################################################################
    #                                SAVE
    ###########################################################################
    def test_save_hyp_data(self):
        """Test saving hypnogram data."""
        sp.saveHypData(filename=self._path_to_tmp('hyp_data.txt'))
        sp.saveHypData(filename=self._path_to_tmp('hyp_data.hyp'))

    def test_save_hyp_figure(self):
        """Test saving hypnogram figure."""
        sp.saveHypFig(filename=self._path_to_tmp('black_and_white.png'))
        sp.saveHypFig(filename=self._path_to_tmp('black_and_white.png'),
                      ascolor=True)

    def test_save_info_table(self):
        """Test saving info table."""
        sp.saveInfoTable(filename=self._path_to_tmp('info_table.txt'))
        sp.saveInfoTable(filename=self._path_to_tmp('info_table.csv'))

    def test_save_scoring_table(self):
        """Test saving scoring table."""
        sp.saveScoringTable(filename=self._path_to_tmp('scoring_table.txt'))
        sp.saveScoringTable(filename=self._path_to_tmp('scoring_table.csv'))

    def test_save_all_detections(self):
        """Test saving all detections."""
        sp.saveAllDetect(filename=self._path_to_tmp('all_detections.npy'))

    def test_save_selected_dection(self):
        """Test saving selected dection."""
        sp.saveSelectDetect(filename=self._path_to_tmp('selected_detect.txt'))
        sp.saveSelectDetect(filename=self._path_to_tmp('selected_detect.csv'))

    def test_save_config(self):
        """Test saving config."""
        sp.saveConfig(filename=self._path_to_tmp('config.txt'))

    def test_save_annotations(self):
        """Test saving annotations."""
        sp.saveAnnotationTable(filename=self._path_to_tmp('annotations.txt'))
        sp.saveAnnotationTable(filename=self._path_to_tmp('annotations.csv'))

    ###########################################################################
    #                                LOAD
    ###########################################################################
    def test_load_hypno(self):
        """Test loading hypno."""
        sp.loadHypno(filename=self._path_to_tmp('hyp_data.txt'))
        sp.loadHypno(filename=self._path_to_tmp('hyp_data.hyp'))

    def test_load_all_detections(self):
        """Test loading all detections."""
        sp.loadDetectAll(filename=self._path_to_tmp('all_detections.npy'))

    def test_load_selected_detection(self):
        """Test loading selected detection."""
        sp.loadDetectSelect(filename=self._path_to_tmp("selected_detect_CZ-"
                                                       "Spindles.txt"))
        sp.loadDetectSelect(filename=self._path_to_tmp("selected_detect_CZ-"
                                                       "Spindles.csv"))

    def test_load_annotations(self):
        """Test loading annotations."""
        # Txt :
        sp.loadAnnotationTable(filename=self._path_to_tmp('annotations.txt'))
        # Csv :
        sp.loadAnnotationTable(filename=self._path_to_tmp('annotations.csv'))
        # Onset only :
        sp.loadAnnotationTable(filename=np.array([10., 20., 3.]))
        # MNE annotations :
        from mne import Annotations
        onset = np.array([10., 20., 3.])
        durations = np.array([1., 1.5, 2.])
        annot = np.array(['Oki1', 'Okinawa', 'Okii'])
        annot = Annotations(onset, durations, annot)
        sp.loadAnnotationTable(filename=annot)

    def test_load_config(self):
        """Test load config."""
        sp.loadConfig(filename=self._path_to_tmp('config.txt'))

    ###########################################################################
    #                             SHORTCUTS
    ###########################################################################

    @staticmethod
    def _key_pressed(canvas, ktype='key_press', key='', **kwargs):
        """Test VisPy KeyEvent."""
        k = KeyEvent(ktype, text=key, **kwargs)
        eval('canvas.events.' + ktype + '(k)')

    @staticmethod
    def _mouse_event(canvas, etype='mouse_press', **kwargs):
        """Test a VisPy mouse event."""
        e = MouseEvent(etype, **kwargs)
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

    ###########################################################################
    #                          DELETE TMP FOLDER
    ###########################################################################

    def test_delete_tmp_folder(self):
        """Delete tmp/folder."""
        shutil.rmtree(path_to_tmp)
