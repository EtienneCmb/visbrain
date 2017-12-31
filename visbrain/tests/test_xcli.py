"""Test command lines."""
import pytest
import os

from click.testing import CliRunner

from visbrain.cli import cli_fig_hyp, cli_sleep_stats, cli_sleep
from visbrain.io import download_file, path_to_visbrain_data
from visbrain.tests._tests_visbrain import _TestVisbrain
# from visbrain.config import CONFIG

# File to load :
sleep_file = path_to_visbrain_data('excerpt2.edf')
hypno_file = path_to_visbrain_data('Hypnogram_excerpt2.txt')

# Download sleep file :
if not os.path.isfile(sleep_file):
    download_file('sleep_edf.zip', unzip=True)


class TestCli(_TestVisbrain):
    """Test cli.py."""

    ###########################################################################
    #                           HYPNO -> FIG
    ###########################################################################
    @pytest.mark.skip('Segmentation fault')
    def test_cli_fig_hyp(self):
        """Test function cli_fig_hyp."""
        import matplotlib
        matplotlib.use('agg')
        runner = CliRunner()
        # Run without output :
        r1 = runner.invoke(cli_fig_hyp, ['-h', hypno_file, '-g', True,
                                         '-c', True, '--dpi', 100])
        # Run with output :
        out = self.to_tmp_dir('hypno.png')
        r2 = runner.invoke(cli_fig_hyp, ['-h', hypno_file, '-g', True,
                                         '-c', True, '-o', out, '--dpi', 100])
        print('Result 1 :', r1.output)
        print('Result 2 :', r2.output)

    @pytest.mark.skip('Segmentation fault')
    def test_cli_sleep_stats(self):
        """Test function cli_sleep_stats."""
        runner = CliRunner()
        out = self.to_tmp_dir('hypno.csv')
        r1 = runner.invoke(cli_sleep_stats, ['-h', hypno_file, '-o', out])
        print('Result : \n', r1.output)

    @pytest.mark.skip('Segmentation fault')
    def test_cli_sleep(self):
        """Test function cli_sleep."""
        runner = CliRunner()
        data = path_to_visbrain_data(sleep_file)
        runner.invoke(cli_sleep, ['-d', data, '-h', hypno_file,
                                  '--show', False])
