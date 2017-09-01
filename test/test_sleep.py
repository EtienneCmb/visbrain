"""Test Sleep module and related methods."""
import os
import shutil
from warnings import warn

import numpy as np
from PyQt5 import QtWidgets

from visbrain import Sleep

# Create a tmp/ directory :
dir_path = os.path.dirname(os.path.realpath(__file__))
path_to_tmp = os.path.join(*(dir_path, 'tmp'))

# Create a random dataset :
sf, nelec, npts = 1000., 8, 100000
data = 10. * np.random.rand(nelec, npts)
channels = ['Cz', 'Fz', 'C1', 'C2', 'C3', 'C4', 'F1', 'other']
hypno = np.random.randint(-1, 3, (npts,))
file, hypno_file = None, None
onset = np.array([100, 2000, 5000])

# Create Sleep application :
app = QtWidgets.QApplication([])
sp = Sleep(file=file, hypno_file=hypno_file, data=data, channels=channels,
           sf=sf, downsample=100., hypno=hypno, axis=False, hedit=True,
           annotation_file=onset)


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

    # ###########################################################################
    # #                                SAVE
    # ###########################################################################
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
        sp.loadDetectSelect(filename=self._path_to_tmp("selected_detect_Cz-"
                                                       "Spindles.txt"))
        sp.loadDetectSelect(filename=self._path_to_tmp("selected_detect_Cz-"
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

    def test_delete_tmp_folder(self):
        """Delete tmp/folder."""
        shutil.rmtree(path_to_tmp)
