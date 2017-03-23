"""Export data into *.txt, *.csv files."""

import csv

__all__ = ['listToCsv', 'listToTxt']


def listToCsv(file, data):
    """Write a csv file.

    Args:
        file: string
            File name for saving file.

        data: list
            List of data to save to the csv file.
    """
    with open(file, 'w') as csvfile:
        writer = csv.writer(csvfile, dialect='excel',
                            quoting=csv.QUOTE_NONNUMERIC)
        for k in data:
            writer.writerow(k)
    return


def listToTxt(file, data):
    """Write a txt file.

    Args:
        file: string
            File name for saving file.

        data: list
            List of data to save to the txt file.
    """
    # Open file :
    ofile = open(file, 'w')
    for k in data:
        ofile.write("%s\n" % ', '.join(k))
    return
