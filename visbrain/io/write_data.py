"""Write data.

- write_npy : Write data as a NumPy (npy) file
- write_npz : Write data as a NumPy (npz) file
- write_mat : Write data as a Matlab (mat) file
- write_txt : Write data as a text (txt) file
- write_csv : Write data as a CSV (csv) file
- write_hyp : Write data as a hyp (hyp) file
"""

__all__ = ['write_npy', 'write_npz', 'write_mat', 'write_txt', 'write_csv',
           'write_hyp']


def write_npy():
    """Write data as a NumPy (npy) file."""
    pass


def write_npz():
    """Write data as a NumPy (npz) file."""
    pass


def write_mat():
    """Write data as a Matlab (mat) file."""
    pass


def write_txt(file, data, delimiter=', '):
    """Write data as a text (txt) file.

    Parameters
    ----------
    file : string
        File name for saving file.
    data : list
        List of data to save to the txt file.
    """
    # Open file :
    ofile = open(file, 'w')
    for k in data:
        ofile.write("%s\n" % delimiter.join(k))
    return


def write_csv(file, data, delimiter=','):
    """Write data as a CSV (csv) file.

    Parameters
    ----------
    file : string
        File name for saving file.
    data : list
        List of data to save to the csv file.
    """
    import csv
    with open(file, 'w') as csvfile:
        writer = csv.writer(csvfile, dialect='excel', delimiter=delimiter)
        for k in data:
            writer.writerow(k)
    return


def write_hyp():
    """Write data as a hyp (hyp) file."""
    pass
