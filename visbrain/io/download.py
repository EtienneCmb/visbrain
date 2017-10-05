"""Download files from dropbox."""
import os
import sys
from urllib import request
import zipfile
from warnings import warn

from .rw_config import load_config_json
from ..utils import verbose


__all__ = ["get_data_url_file", "download_file"]


def get_data_url_file():
    """Get path to the data_url.txt file."""
    dirfile = sys.modules[__name__].__file__.split('download')[0]
    return load_config_json(os.path.join(dirfile, 'data_url.txt'))


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


def download_file(name, filename=None, to_path=None,
                  unzip=False, remove_archive=False):
    """Download a file.

    Parameters
    ----------
    name : string
        Name of the file to download or url.
    filename : string | None
        Name of the file to be saved in case of url.
    """
    print('\n----------------------------------------------------------------')
    if bool(name.find('http') + 1):
        assert isinstance(filename, str)
        url = name
    else:
        filename, url = name, get_data_url(name)
    to_path = os.getcwd() if not isinstance(to_path, str) else to_path
    path_to_file = os.path.join(to_path, filename)
    to_download = not os.path.isfile(path_to_file)

    # Dowload file if needed :
    if to_download:
        verbose('Downloading ' + path_to_file, level='info')
        # Check if directory exists else creates it
        if not os.path.exists(to_path):
            verbose('Foler ' + to_path + ' created', level='info')
            os.makedirs(to_path)
        # Download file :
        fh, _ = request.urlretrieve(url, path_to_file, reporthook=reporthook)
        # Unzip file :
        if unzip:
            # Unzip archive :
            zip_file_object = zipfile.ZipFile(fh, 'r')
            zip_file_object.extractall(path=to_path)
            zip_file_object.close()
            verbose('Unzip file', level='info')
            if remove_archive:  # Remove archive :
                verbose('Archive' + path_to_file + ' removed', level='warning')
                os.remove(path_to_file)
    else:
        verbose("File already dowloaded (" + path_to_file + ").", level='info')
    print('----------------------------------------------------------------\n')
