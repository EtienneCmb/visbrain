"""Test command lines."""
import os
import shutil
from PyQt5 import QtWidgets

from click.testing import CliRunner

from visbrain.io import download_file
from visbrain.cli import cli_fig_hyp, cli_sleep_stats, cli_sleep
from visbrain.utils import verbose

# Create a tmp/ directory :
dir_path = os.path.dirname(os.path.realpath(__file__))
path_to_tmp = os.path.join(*(dir_path, 'tmp'))


def path_to_edf(name):
    """Get path to the edf file."""
    return os.path.join(path_to_tmp, name)


class TestCli(object):
    """Test cli.py."""

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

    def test_download_file(self):
        """Download the EDF dataset."""
        download_file('sleep_edf.zip', to_path=path_to_tmp, unzip=True)

    ###########################################################################
    #                           HYPNO -> FIG
    ###########################################################################
    def test_cli_fig_hyp(self):
        """Test function cli_fig_hyp."""
        import matplotlib
        matplotlib.use('agg')
        runner = CliRunner()
        hypno = self._path_to_tmp('Hypnogram_excerpt2.txt')
        # Run without output :
        r1 = runner.invoke(cli_fig_hyp, ['-h', hypno, '-g', True, '-c', True])
        # Run with output :
        out = self._path_to_tmp('hypno.png')
        r2 = runner.invoke(cli_fig_hyp, ['-h', hypno, '-g', True, '-c', True,
                           '-o', out])
        print('Result 1 :', r1.output)
        print('Result 2 :', r2.output)

    def test_cli_sleep_stats(self):
        """Test function cli_sleep_stats."""
        runner = CliRunner()
        hypno = self._path_to_tmp('Hypnogram_excerpt2.txt')
        out = self._path_to_tmp('hypno.csv')
        r1 = runner.invoke(cli_sleep_stats, ['-h', hypno, '-o', out])
        print('Result : \n', r1.output)

    def test_cli_sleep(self):
        """Test function cli_sleep."""
        verbose('test_cli_sleep not configured properly', level=Warning)
        # runner = CliRunner()
        # data = self._path_to_tmp('excerpt2.edf')
        # hypno = self._path_to_tmp('Hypnogram_excerpt2.txt')
        # app = QtWidgets.QApplication([])
        # runner.invoke(cli_sleep, ['-d', data, '-h', hypno, '--show', False])
        # app.quit()
        # del app

    def test_delete_tmp_folder(self):
        """Delete tmp/folder."""
        shutil.rmtree(path_to_tmp)
