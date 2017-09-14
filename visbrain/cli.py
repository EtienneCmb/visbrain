"""Command-line control of visbrain."""
import click
from visbrain import Sleep

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
