"""Command-line control of visbrain."""
import click
from visbrain import Sleep
from visbrain.io import (write_fig_hyp, read_hypno, oversample_hypno, write_csv)
from visbrain.utils import batch_sleepstats
import os.path
import numpy as np

###############################################################################
#                                  SLEEP
###############################################################################

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
@click.option('-a', '--annotation_file', default=None,
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
def cli_sleep(data, hypno, config_file, annotation_file, downsample, use_mne,
              preload, show):
    """Open Sleep using command-line."""
    # File conversion :
    if data is not None:
        data = click.format_filename(data)
    if hypno is not None:
        hypno = click.format_filename(hypno)
    if config_file is not None:
        config_file = click.format_filename(config_file)
    if annotation_file is not None:
        annotation_file = click.format_filename(annotation_file)
    s = Sleep(data=data, hypno=hypno, downsample=downsample,
              use_mne=use_mne, preload=preload, config_file=config_file,
              annotation_file=annotation_file)
    if show:
        s.show()

@click.command()
@click.option('-h', '--hypno', default=None,
              help='Name of the hypnogram file to load (with extension).',
              type=click.Path(exists=True))
@click.option('-g', '--grid', default=False,
              help='Add X and Y grids to figure. Default is False.',
              type=bool)
@click.option('-c', '--color', default=False,
              help='Plot in black or white (False) or in color (True). Default is False.',
              type=bool)
@click.option('-o', '--outfile', default=None,
              help='Output filename (with extension).',
              type=click.Path(exists=False))
@click.option('--dpi', default=300,
              help='Dots per inches. Larger dpi will result in larger figure resolution. Default is 300.',
              type=int)
def cli_fig_hyp(hypno, grid, color, outfile, dpi):
    """Create hypnogram figure from hypnogram file"""
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
        time_base = 1 / sf_hyp
        hypno = oversample_hypno(hypno, len(hypno) * time_base)
        sf_hyp = 1
    # Create figure
    write_fig_hyp(outfile, hypno, sf=sf_hyp, tstartsec=0, grid=grid, ascolor=color, dpi=dpi)
    print('Hypnogram figure saved to:', outfile)


@click.command()
@click.option('-h', '--hypno', default=None,
              help='Name of the hypnogram file to load (with extension).',
              type=click.Path(exists=True))
@click.option('-o', '--outfile', default=None,
              help='Output filename (with extension *.txt / *.csv).',
              type=click.Path(exists=False))
def cli_sleep_stats(hypno, outfile):
    """Compute and export sleep statistics from hypnogram file"""
    # File conversion :
    if hypno is not None:
        hypno_path = click.format_filename(hypno)
    if outfile is not None:
        outfile = click.format_filename(outfile)
        ext = os.path.splitext(outfile)[1][1:].strip().lower()
        if ext == '':
            outfile = outfile + '.csv'
    else:
        outfile = hypno_path + '.csv'
    # Load hypnogram
    hypno, sf_hyp = read_hypno(hypno_path)
    if sf_hyp < 1:
        time_base = 1 / sf_hyp
        hypno = oversample_hypno(hypno, len(hypno) * time_base)
        sf_hyp = 1

    stats = batch_sleepstats(hypno, sf_hyp=sf_hyp)
    stats['File_0'] = hypno_path
    print('\nSLEEP STATS\n===========')
    keys, val = [''] * len(stats), [''] * len(stats)
    # Fill table :
    for num, (k, v) in enumerate(stats.items()):
        # Get keys and row :
        key, r = k.split('_')
        print(key, '\t', str(v))
        # Remember variables :
        keys[int(r)] = key
        val[int(r)] = str(v)
    write_csv(outfile, zip(keys, val))
    print('===========\nCSV file saved to:', outfile)
