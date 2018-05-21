"""Command-line control of visbrain."""
from __future__ import print_function
import click
import os.path
import numpy as np

from visbrain import Sleep
from visbrain.io import (write_fig_hyp, read_hypno, oversample_hypno,
                         write_csv)
from visbrain.utils import sleepstats

###############################################################################
#                                  SLEEP
###############################################################################

# -------------------- SLEEP GUI --------------------


@click.command()
@click.option('-d', '--data', default=None,
              help='Name of the  polysomnographic file to load.',
              type=click.Path(exists=True))
@click.option('-h', '--hypno', default=None,
              help='Name of the hypnogram file to load.',
              type=click.Path(exists=True))
@click.option('-c', '--config_file', default=None,
              help='Path to a configuration file.',
              type=click.Path(exists=True))
@click.option('-a', '--annotations', default=None,
              help='Path to an annotation file.',
              type=click.Path(exists=True))
@click.option('--downsample', default=100.,
              help='Down-sampling frequency. Default is 100.')
@click.option('--use_mne', default=False,
              help='Load your file using MNE-python. Default is False.',
              type=bool)
@click.option('--preload', default=True,
              help='Preload data in memory. Default is True', type=bool)
@click.option('--show', default=True,
              help='Display GUI. Default is True', type=bool)
def cli_sleep(data, hypno, config_file, annotations, downsample, use_mne,
              preload, show):
    """Open the graphical user interface of Sleep."""
    # File conversion :
    if data is not None:
        data = click.format_filename(data)
    if hypno is not None:
        hypno = click.format_filename(hypno)
    if config_file is not None:
        config_file = click.format_filename(config_file)
    if annotations is not None:
        annotations = click.format_filename(annotations)
    s = Sleep(data=data, hypno=hypno, downsample=downsample,
              use_mne=use_mne, preload=preload, config_file=config_file,
              annotations=annotations)
    if show:
        s.show()

# -------------------- HYPNOGRAM TO FIGURE --------------------


@click.command()
@click.option('-h', '--hypno', default=None,
              help='Name of the hypnogram file to load (with extension).',
              type=click.Path(exists=True))
@click.option('-g', '--grid', default=False,
              help='Add X and Y grids to figure. Default is False.',
              type=bool)
@click.option('-c', '--color', default=False,
              help='Get colored figure. Default is False (black and white).',
              type=bool)
@click.option('-o', '--outfile', default=None,
              help='Output filename (with extension).',
              type=click.Path(exists=False))
@click.option('--dpi', default=300,
              help='Dots per inches (resolution). Default is 300.',
              type=int)
def cli_fig_hyp(hypno, grid, color, outfile, dpi):
    """Create hypnogram figure from hypnogram file."""
    # File conversion :
    if hypno is not None:
        hypno = click.format_filename(hypno)
    if outfile is not None:
        outfile = click.format_filename(outfile)
        ext = os.path.splitext(outfile)[1][1:].strip().lower()
        if ext == '':
            outfile = outfile + '.png'
    else:
        outfile = hypno + '.png'
    # Load hypnogram
    hypno, sf_hyp = read_hypno(hypno)
    # Bad cases (e.g. EDF files from DreamBank.net)
    if sf_hyp < 1:
        mult = int(np.round(len(hypno) / sf_hyp))
        hypno = oversample_hypno(hypno, mult)
        sf_hyp = 1
    # Create figure
    write_fig_hyp(hypno, sf=sf_hyp, file=outfile, start_s=0., grid=grid,
                  ascolor=color, dpi=dpi)
    print('Hypnogram figure saved to:', outfile)


# -------------------- SLEEP STATS --------------------

@click.command()
@click.option('-h', '--hypno', default=None,
              help='Name of the hypnogram file to load (with extension).',
              type=click.Path(exists=True))
@click.option('-o', '--outfile', default=None,
              help='Output filename (with extension - *.csv). If None, sleep \
              statistics will only be displayed and not saved into a file',
              type=click.Path(exists=False))
def cli_sleep_stats(hypno, outfile):
    """Compute sleep statistics from hypnogram file and export them in csv.

    Sleep statistics specifications:

    * Time in Bed (TIB) : total duration of the hypnogram.
    * Total Dark Time (TDT) : duration of the hypnogram from beginning
      to last period of sleep.
    * Sleep Period Time (SPT) : duration from first to last period of sleep.
    * Wake After Sleep Onset (WASO) : duration of wake periods within SPT
    * Sleep Efficiency (SE) : TST / TDT * 100 (%).
    * Total Sleep Time (TST) : SPT - WASO.
    * W, N1, N2, N3 and REM: sleep stages duration.
    * % (W, ... REM) : sleep stages duration expressed in percentages of TDT.
    * Latencies: latencies of sleep stages from the beginning of the record.

    (All values except SE and percentages are expressed in minutes)
    """
    # File conversion :
    if hypno is not None:
        hypno_path = click.format_filename(hypno)
    if outfile is not None:
        outfile = click.format_filename(outfile)
        # Check extension
        ext = os.path.splitext(outfile)[1][1:].strip().lower()
        if ext == '':
            outfile = outfile + '.csv'

    # Load hypnogram
    hypno, sf_hyp = read_hypno(hypno_path)
    if sf_hyp < 1:
        mult = int(np.round(len(hypno) / sf_hyp))
        hypno = oversample_hypno(hypno, mult)
        sf_hyp = 1

    # Get sleep stats
    stats = sleepstats(hypno, sf_hyp=sf_hyp)
    stats['File'] = hypno_path
    print('\nSLEEP STATS\n===========')
    keys, val = [''] * len(stats), [''] * len(stats)
    # Fill table :
    for num, (k, v) in enumerate(stats.items()):
        print(k, '\t', str(v))
        # Remember variables :
        keys[int(num)] = k
        val[int(num)] = str(v)
    if outfile is not None:
        write_csv(outfile, zip(keys, val))
        print('===========\nCSV file saved to:', outfile)
