"""Download files from dropbox."""
import logging
import os
import sys
from urllib import request
import zipfile
from warnings import warn

from .rw_config import load_config_json
from .path import get_data_path


logger = logging.getLogger('visbrain')


__all__ = ["get_data_url_file", "download_file"]


def get_data_url_file():
    """Get path to the data_url.txt file."""
    return load_config_json(get_data_path(file='data_url.txt'))


def get_data_url(name):
    """Get filename and url to a file.

    Parameters
    ----------
    name : string
        Name of the file.

    Returns
    -------
    url : string
        Url to the file to download.
    """
    # Get path to data_url.txt :
    urls = get_data_url_file()
    # Try to get the file :
    try:
        url_to_download = urls[name]
        if not bool(url_to_download.find('dl=1') + 1):
            warn("The dropbox url should contains 'dl=1'.")
        return urls[name]
    except:
        raise IOError(name + " not in the default path list of files.")


def reporthook(blocknum, blocksize, totalsize):
    """Report downloading status."""
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = min(100, readsofar * 1e2 / totalsize)
        s = "\rSTATUS : %5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        if readsofar >= totalsize:  # near the end
            sys.stderr.write("\n")
    else:  # total size is unknown
        sys.stderr.write("\rread %d" % (readsofar,))


def download_file(name, filename=None, to_path=None, unzip=False,
                  remove_archive=False, use_pwd=False):
    """Download a file.

    By default this function download a file to ~/visbrain_data.

    Parameters
    ----------
    name : string
        Name of the file to download or url.
    filename : string | None
        Name of the file to be saved in case of url.
    to_path : string | None
        Download file to the path specified.
    unzip : bool | False
        Unzip archive if needed.
    remove_archive : bool | False
        Remove archive after unzip.
    use_pwd : bool | False
        Download the file to the current directory.

    Returns
    -------
    path_to_file : string
        Path to the downloaded file.
    """
    # Default visbrain-path to data (HOME/visbrain_data):
    vb_path = os.path.join(os.path.expanduser('~'), 'visbrain_data')
    vb_path = os.getcwd() if use_pwd else vb_path
    if bool(name.find('http') + 1):
        if filename is None:
            filename = os.path.split(name)[1]
        assert isinstance(filename, str)
        url = name
    else:
        filename, url = name, get_data_url(name)
    to_path = vb_path if not isinstance(to_path, str) else to_path
    path_to_file = os.path.join(to_path, filename)
    to_download = not os.path.isfile(path_to_file)

    # Dowload file if needed :
    if to_download:
        logger.info('Downloading %s' % path_to_file)
        # Check if directory exists else creates it
        if not os.path.exists(to_path):
            logger.info('Folder %s created' % to_path)
            os.makedirs(to_path)
        # Download file :
        fh, _ = request.urlretrieve(url, path_to_file, reporthook=reporthook)
        # Unzip file :
        if unzip:
            # Unzip archive :
            zip_file_object = zipfile.ZipFile(fh, 'r')
            zip_file_object.extractall(path=to_path)
            zip_file_object.close()
            logger.info('Unzip archive')
            if remove_archive:  # Remove archive :
                logger.info('Archive %s removed' % path_to_file)
                os.remove(path_to_file)
    else:
        logger.info("File already dowloaded (%s)." % path_to_file)
    return path_to_file
