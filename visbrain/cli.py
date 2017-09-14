"""Command-line control of visbrain."""
from __future__ import print_function
import click
from visbrain import Sleep
from visbrain.io import (write_fig_hyp, read_hypno)
import os.path
import numpy as np

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

# -------------------- HYPNOGRAM TO FIGURE --------------------


@click.command()
@click.option('-h', '--hypno', default=None,
              help="Path to the hypnogram file (*.hyp) to load.",
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
        ext = os.path.splitext(hypno)[1][1:].strip().lower()
        assert(ext == 'hyp')
    if outfile is not None:
        outfile = click.format_filename(outfile)
        ext = os.path.splitext(outfile)[1][1:].strip().lower()
        if ext == '':
            outfile = outfile + '.png'
    else:
        outfile = hypno + '.png'
    # Load hypnogram
    hyp = np.genfromtxt(hypno, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0)
    hyp = np.char.decode(hyp)
    # Sampling rate of hypnogram files
    sf = float(hyp[0].split()[1])
    # Extract hypnogram values
    hypval = np.array(hyp[4:], dtype=np.int)
    # Replace values according to Iber et al 2007
    hypval[hypval == -2] = -1
    hypval[hypval == 4] = 3
    hypval[hypval == 5] = 4
    # Create figure
    write_fig_hyp(outfile, hypval, sf=sf, tstartsec=0, grid=grid,
                  ascolor=color, dpi=dpi)
    print('Hypnogram figure saved to:', outfile)
