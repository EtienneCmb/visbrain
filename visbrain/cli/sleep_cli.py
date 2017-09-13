import click
from visbrain import Sleep


@click.command()
@click.option('--data', default=None,
              help='Name of the  polysomnographic file to load.')
@click.option('--hypno', default=None,
              help='Name of the hypnogram file to load.')
@click.option('--use_mne', default=False,
              help='Load your file using MNE-python. Default is False.',
              type=bool)
@click.option('--preload', default=True,
              help='Preload data in memory. Default is True', type=bool)
@click.option('--show', default=True,
              help='Display GUI. Default is True', type=bool)
def cli(data, hypno, use_mne, preload, show):
    """Open Sleep using command-line."""
    s = Sleep(data=data, hypno=hypno, use_mne=use_mne, preload=preload)
    if show:
        s.show()
