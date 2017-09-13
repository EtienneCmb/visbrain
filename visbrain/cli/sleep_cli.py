import click
from visbrain import Sleep


@click.command()
@click.option('--data', default=None,
              help='Name of the  polysomnographic file to load.')
@click.option('--hypno', default=None,
              help='Name of the hypnogram file to load.')
@click.option('--downsample', default=100.,
              help='Down-sampling frequency. Default is 100.')
@click.option('--use_mne', default=False,
              help='Load your file using MNE-python. Default is False.',
              type=bool)
@click.option('--preload', default=True,
              help='Preload data in memory. Default is True', type=bool)
@click.option('--show', default=True,
              help='Display GUI. Default is True', type=bool)
@click.option('--config_file', default=None,
              help='Path to a configuration file.')
@click.option('--annotation_file', default=None,
              help='Path to an annotation file.')
def cli(data, hypno, downsample, use_mne, preload, show, config_file,
        annotation_file):
    """Open Sleep using command-line."""
    s = Sleep(data=data, hypno=hypno, downsample=downsample,
              use_mne=use_mne, preload=preload, config_file=config_file,
              annotation_file=annotation_file)
    if show:
        s.show()

# if __name__ == '__main__':
#     data = '/media/etienne/E438C4AE38C480D2/Users/Etienne Combrisson/Mes documents/suj1 session2_detected_0.95.edf'
#     cli(['--data', data])
