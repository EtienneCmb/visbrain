import os
import shutil
import numpy as np
import pytest

from visbrain.io.dependencies import is_mne_installed, is_nibabel_installed
from visbrain.io.download import get_data_url_file, download_file
from visbrain.io.mneio import mne_switch
from visbrain.io.read_annotations import (annotations_to_array,
                                          merge_annotations)
from visbrain.io.rw_config import save_config_json, load_config_json
from visbrain.io.rw_hypno import (oversample_hypno, write_hypno_txt,
                                  write_hypno_hyp, read_hypno, read_hypno_hyp,
                                  read_hypno_txt)
from visbrain.io.rw_utils import get_file_ext, safety_save
from visbrain.io.read_data import (read_mat, read_pickle, read_npy, read_npz,
                                   read_txt, read_csv, read_json, read_nifti,
                                   read_stc)
from visbrain.io.write_data import (write_csv, write_txt)


# Create a tmp/ directory :
dir_path = os.path.dirname(os.path.realpath(__file__))
path_to_tmp = os.path.join(*(dir_path, 'tmp'))


class TestIO(object):
    """Test function in dependencies.py."""

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
    #                                DOWNLOAD
    ###########################################################################
    def test_get_data_url_file(self):
        """Test function get_data_url_file."""
        get_data_url_file()

    def test_download_file(self):
        """Test function download_file."""
        download_file('Px.npy', to_path=path_to_tmp)

    def test_download_custom_url(self):
        """Test function download_custom_url."""
        name = "https://www.dropbox.com/s/whogfxutyxoir1t/xyz_sample.npz?dl=1"
        download_file(name, filename="text.npz", to_path=path_to_tmp)

    @pytest.mark.skip("Test downloading all files is too slow")
    def test_download_files_from_dropbox(self):
        """Test function download_file from dropbox."""
        urls = get_data_url_file()
        for name in list(urls.keys()):
            download_file(name, to_path=path_to_tmp)

    ###########################################################################
    #                              MNE I/O
    ###########################################################################

    @pytest.mark.slow
    def test_mne_switch(self):
        """Test function mne_switch."""
        download_file('sleep_edf.zip', to_path=path_to_tmp, unzip=True)
        to_exclude = ['VAB', 'NAF2P-A1', 'PCPAP', 'POS', 'FP2-A1', 'O2-A1',
                      'CZ2-A1', 'event_pneumo', 'event_pneumo_aut']
        kwargs = dict(exclude=to_exclude, stim_channel=False)
        mne_switch(self._path_to_tmp('excerpt2'), '.edf', 100., preload=True,
                   **kwargs)

    ###########################################################################
    #                              ANNOTATIONS
    ###########################################################################

    @staticmethod
    def _get_annotations(dtype=float, n=10, as_list=False):
        start = np.random.rand(n).astype(dtype)
        end = np.random.rand(n).astype(dtype)
        text = ['Annotation ' + str(k) for k in range(n)]
        if as_list:
            return list(start), list(end), list(text)
        else:
            return start, end, text

    def _get_annotation_type(self):
        from mne import Annotations
        one_d = self._get_annotations(as_list=False)[0]
        one_d_list = self._get_annotations(as_list=True)[0]
        three_d = np.c_[self._get_annotations()]
        csv = self._path_to_tmp('annotations.csv')
        txt = self._path_to_tmp('annotations.txt')
        mne = Annotations(*self._get_annotations())
        return one_d, one_d_list, three_d, csv, txt, mne

    def test_write_annotations(self):
        """Test function write_annotations."""
        start, end, text = self._get_annotations(str, as_list=True)
        write_csv(self._path_to_tmp('annotations.csv'), zip(start, end, text))
        write_txt(self._path_to_tmp('annotations.txt'), zip(start, end, text))

    def test_annotations_to_array(self):
        """Test function annotations_to_array."""
        for k in self._get_annotation_type():
            annotations_to_array(k)

    def test_merge_annotations(self):
        """Test function merge_annotations."""
        merge_annotations(*(None, *self._get_annotation_type()))

    ###########################################################################
    #                                CONFIG
    ###########################################################################

    @staticmethod
    def _get_config():
        config = {'Button1': True, 'Button2': 1, 'Button3': None}
        return config

    def test_save_config_json(self):
        """Test function save_config_json."""
        save_config_json(self._path_to_tmp('config.txt'), self._get_config())

    def test_load_config_json(self):
        """Test function load_config_json."""
        config = load_config_json(self._path_to_tmp('config.txt'))
        assert config == self._get_config()

    ###########################################################################
    #                              DEPENDENCIES
    ###########################################################################

    def test_is_mne_installed(self):
        """Test is_mne_installed function."""
        assert is_mne_installed()

    def test_is_nibabel_installed(self):
        """Test function is_nibabel_installed."""
        assert is_nibabel_installed()

    ###########################################################################
    #                                 HYPNO
    ###########################################################################

    @staticmethod
    def _get_hypno():
        return np.array([-1, 4, 2, 3, 0])

    def test_oversample_hypno(self):
        """Test function oversample_hypno."""
        hyp = self._get_hypno()
        hyp_over = oversample_hypno(hyp, 12)
        to_hyp = np.array([-1, -1, 4, 4, 2, 2, 3, 3, 0, 0, 0, 0])
        assert np.array_equal(hyp_over, to_hyp)

    def test_write_hypno_txt(self):
        """Test function write_hypno_txt."""
        hyp = self._get_hypno()
        write_hypno_txt(self._path_to_tmp('hyp.txt'), hyp, 100., 1000., 5000)

    def test_write_hypno_hyp(self):
        """Test function write_hypno_hyp."""
        hyp = self._get_hypno()
        write_hypno_hyp(self._path_to_tmp('hyp.hyp'), hyp, 100., 1000., 5000)

    def test_read_hypno(self):
        """Test function read_hypno."""
        # TXT version :
        hyp_txt, sf_txt = read_hypno(self._path_to_tmp('hyp.txt'))
        # HYP version :
        hyp_hyp, sf_hyp = read_hypno(self._path_to_tmp('hyp.hyp'))
        assert np.array_equal(hyp_txt, hyp_hyp)
        assert sf_txt == sf_hyp

    def test_read_hypno_hyp(self):
        """Test function read_hypno_hyp."""
        read_hypno_hyp(self._path_to_tmp('hyp.hyp'))

    def test_read_hypno_txt(self):
        """Test function read_hypno_txt."""
        read_hypno_txt(self._path_to_tmp('hyp.txt'))

    def test_get_file_ext(self):
        """Test function get_file_ext."""
        file, ext = get_file_ext(self._path_to_tmp('hyp.txt'))
        assert file[-1] != '.'
        assert ext == '.txt'

    def test_safety_save(self):
        """Test function safety_save."""
        file = safety_save(self._path_to_tmp('hyp.txt'))
        file_txt, _ = get_file_ext(self._path_to_tmp('hyp.txt'))
        assert file == file_txt + '(1).txt'

    ###########################################################################
    #                              READ
    ###########################################################################

    def test_read_stc(self):
        """Test function read_stc."""
        download_file("meg_source_estimate-lh.stc", to_path=path_to_tmp)
        read_stc(self._path_to_tmp("meg_source_estimate-lh.stc"))

    @pytest.mark.slow
    def test_read_nifti(self):
        """Test function read_nifti."""
        download_file("GG-853-GM-0.7mm.nii.gz", to_path=path_to_tmp)
        read_nifti(self._path_to_tmp("GG-853-GM-0.7mm.nii.gz"))

    def test_delete_tmp_folder(self):
        """Delete tmp/folder."""
        shutil.rmtree(path_to_tmp)
