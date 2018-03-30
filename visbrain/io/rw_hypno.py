"""write/Read hypnogram data.

- write_hypno_txt : as text file
- write_hypno_hyp : as hyp file
- read_hypno : read either *.hyp or *.txt hypnogram data
- read_hypno_hyp : load *.hyp hypnogram data
- read_hypno_txt : load *.txt hypnogram data
"""
import numpy as np
import os

from ..utils import vispy_array

__all__ = ('oversample_hypno', 'write_hypno_txt', 'write_hypno_hyp',
           'read_hypno', 'read_hypno_hyp', 'read_hypno_txt')


def oversample_hypno(hypno, n):
    """Oversample hypnogram.

    Parameters
    ----------
    hypno : array_like
        Hypnogram data of shape (N,) with N < n.
    n : int
        The destination length.

    Returns
    -------
    hypno : array_like
        The hypnogram of shape (n,)
    """
    # Get the repetition number :
    rep_nb = float(np.floor(n / len(hypno)))

    # Repeat hypnogram :
    hypno = np.repeat(hypno, rep_nb)
    npts = len(hypno)

    # Check size
    if npts < n:
        hypno = np.append(hypno, hypno[-1] * np.ones((n - npts)))
    elif n > npts:
        raise ValueError("The length of the hypnogram  vector must "
                         "be " + str(n) + " (Currently : " + str(npts) + ".")

    return hypno.astype(int)


def write_hypno_txt(filename, hypno, sf, sfori, n, window=1.):
    """Save hypnogram in txt file format (txt).

    Header is in file filename_description.txt

    Parameters
    ----------
    filename : str
        Filename (with full path) of the file to save
    hypno : array_like
        Hypnogram array, same length as data
    sf : float
        Sampling frequency of the data (after downsampling)
    sfori : int
        Original sampling rate of the raw data
    n : int
        Original number of points in the raw data
    window : float | 1
        Time window (second) of each point in the hypno
        Default is one value per second
        (e.g. window = 30 = 1 value per 30 second)
    """
    base = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    descript = os.path.join(dirname, os.path.splitext(
        base)[0] + '_description.txt')

    # Save hypno
    step = int(hypno.shape / np.round(n / sfori))
    np.savetxt(filename, hypno[::step].astype(int), fmt='%s')

    # Save header file
    hdr = np.array([['time ' + str(window)], ['W 0'], ['N1 1'], ['N2 2'],
                    ['N3 3'], ['REM 4'], ['Art -1']]).flatten()
    np.savetxt(descript, hdr, fmt='%s')


def write_hypno_hyp(filename, hypno, sf, sfori, n):
    """Save hypnogram in Elan file format (hyp).

    Parameters
    ----------
    filename : str
        Filename (with full path) of the file to save
    hypno : array_like
        Hypnogram array, same length as data
    sf : int
        Sampling frequency of the data (after downsampling)
    sfori : int
        Original sampling rate of the raw data
    n : int
        Original number of points in the raw data
    """
    # Check data format
    sf = int(sf)
    hypno = hypno.astype(int)
    hypno[hypno == 4] = 5
    step = int(hypno.shape / np.round(n / sfori))

    hdr = np.array([['time_base 1.000000'],
                    ['sampling_period ' + str(np.round(1 / sfori, 8))],
                    ['epoch_nb ' + str(int(n / sfori))],
                    ['epoch_list']]).flatten()

    # Save
    export = np.append(hdr, hypno[::step].astype(str))
    np.savetxt(filename, export, fmt='%s')


def read_hypno(path):
    """Load hypnogram file.

    Sleep stages in the hypnogram should be scored as follow
    see Iber et al. 2007

    Wake:   0
    N1:     1
    N2:     2
    N3:     3
    REM:    4
    Art:    -1  (optional)

    Parameters
    ----------
    path : string
        Filename (with full path) to hypnogram file.

    Returns
    -------
    hypno : array_like
        The hypnogram vector in its original length.

    sf_hyp: float
        The hypnogram original sampling frequency (Hz)
    """
    # Test if file exist :
    assert os.path.isfile(path)

    # Extract file extension :
    file, ext = os.path.splitext(path)

    # Load the hypnogram :
    if ext == '.hyp':  # ELAN
        hypno, sf_hyp = read_hypno_hyp(path)
    elif ext in ['.txt', '.csv']:  # TXT / CSV
        hypno, sf_hyp = read_hypno_txt(path)

    return vispy_array(hypno), sf_hyp


def read_hypno_hyp(path):
    """Read Elan hypnogram (hyp).

    Parameters
    ----------
    path : str
        Filename(with full path) to Elan .hyp file

    Returns
    -------
    hypno : array_like
        The hypnogram vector in its original length.
    sf_hyp : float
        The hypnogram original sampling frequency (Hz)
    """
    hyp = np.genfromtxt(path, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0)

    hyp = np.char.decode(hyp)

    # Get sampling frequency of hypnogram
    sf_hyp = 1 / float(hyp[0].split()[1])

    # Extract hypnogram values
    hypno = np.array(hyp[4:], dtype=np.int)

    # Replace values according to Iber et al 2007
    hypno[hypno == -2] = -1
    hypno[hypno == 4] = 3
    hypno[hypno == 5] = 4

    return hypno, sf_hyp


def read_hypno_txt(path):
    """Read text files (.txt / .csv) hypnogram.

    Parameters
    ----------
    path : str
        Filename(with full path) to hypnogram(.txt)

    Returns
    -------
    hypno : array_like
        The hypnogram vector in its original length.
    sf_hyp : float
        The hypnogram original sampling frequency (Hz)
    """
    assert os.path.isfile(path)

    file, ext = os.path.splitext(path)

    header = file + '_description.txt'
    assert os.path.isfile(header)

    # Load header file
    labels = np.genfromtxt(header, dtype=str, delimiter=" ", usecols=0)
    values = np.genfromtxt(header, dtype=float, delimiter=" ", usecols=1)
    desc = {label: row for label, row in zip(labels, values)}

    # Get sampling frequency of hypnogram
    sf_hyp = 1 / float(desc['time'])

    # Load hypnogram file
    hyp = np.genfromtxt(path, delimiter='\n', usecols=[0],
                        dtype=None, skip_header=0)

    if not np.issubdtype(hyp.dtype, np.integer):
        hyp = np.char.decode(hyp)
        hypno = np.array([s for s in hyp if s.lstrip('-').isdigit()],
                         dtype=int)
    else:
        hypno = hyp.astype(int)

    hypno = swap_hyp_values(hypno, desc)

    return hypno, sf_hyp


def swap_hyp_values(hypno, desc):
    """Swap values in hypnogram vector.

    Sleep stages in the hypnogram should be scored as follow
    see Iber et al. 2007

    e.g from the DREAM bank EDF database
    Stage   Orig. val    New val
    W       5           0
    N1      3           1
    N2      2           2
    N3      1           3
    REM     0           4

    Parameters
    ----------
    hypno : array_like
        The hypnogram vector
    description : str
        Path to a .txt file containing labels and values of each sleep
        stage separated by a space

    Returns
    -------
    hypno_s : array_like
        Hypnogram with swapped values
    """
    # Swap values
    hypno_s = -1 * np.ones(shape=(hypno.shape), dtype=int)

    if 'Art' in desc:
        hypno_s[hypno == desc['Art']] = -1
    if 'Nde' in desc:
        hypno_s[hypno == desc['Nde']] = -1
    if 'Mt' in desc:
        hypno_s[hypno == desc['Mt']] = -1
    if 'W' in desc:
        hypno_s[hypno == desc['W']] = 0
    if 'N1' in desc:
        hypno_s[hypno == desc['N1']] = 1
    if 'N2' in desc:
        hypno_s[hypno == desc['N2']] = 2
    if 'N3' in desc:
        hypno_s[hypno == desc['N3']] = 3
    if 'N4' in desc:
        hypno_s[hypno == desc['N4']] = 3
    if 'REM' in desc:
        hypno_s[hypno == desc['REM']] = 4

    return hypno_s

def read_hypno_edf(hypno,file):
    """This function is developed to read hypnogram files which are formatted according 
       to EDF+ specifications (see https://www.edfplus.info/specs/index.html).
       The function was specifically developed to read and plot hypnograms which are
       part of the Physionet Sleep Database (see https://physionet.org/pn4/sleep-edfx/). 
       The Physionet Sleep Database contains 61 polysomnograms (PSGs) with accompanying hypnograms.
       The Physionet polysomnogram files are using edf format, while the hypnograms use
       EDF+. When using EDF+ for hypnograms, the data records contain Timestamped Annotation
       Lists (TALs). Each TAL consists of an onset, a duration, and a sleep stage.
       The following assumptions have been made:
       - the scoring period for the hypnogram is equal to the number of seconds per data record as 
         given by header information of the accompanying polysomnogram file
       - all EDF+ hypnogram files use the same scoring for sleep stages which are in the function
         converted to the values used by Visbrain:
           EDF+ score                value used by Visbrain
         Sleep stage ?                      -1
         Movement time                      -1
         Sleep stage W                       0
         Sleep stage 1                       1
         Sleep stage 2                       2
         Sleep stage 3                       3
         Sleep stage 4                       3
         Sleep stage R                       4
         
    The Physionet hypnogram files (EDF+) sometimes cover a slightly longer total period than the 
    polysomnograph files, where the score for the last part is set to "Sleep stage ?". This function
    will only read the hypnogram files so that only the time period of the polysomnograph is covered.  
    
    The function will check whether the hypnogram file is the appropriate accompanying file to the
    polysomnogranph file by comparing the "subjcet_id" as well as the "recording_id" of the two files.
    """

    with open(file + '.edf', 'rb') as f:                                 # open edf data file
        hdr1 = {}
        assert f.tell() == 0
        assert f.read(8) == b'0       '

        # recording info
        hdr1['subject_id'] = f.read(80).decode('utf-8').strip()   # read patient info
        hdr1['recording_id'] = f.read(80).decode('utf-8').strip() # read recording date and time

        f.seek(68,1)
        hdr1['n_records'] = int(f.read(8))
        hdr1['record_length'] = float(f.read(8))  # in seconds 
        end_file = str(int(hdr1['n_records']*hdr1['record_length']) )

    with open(hypno, 'rb') as f:                                 # open edf hypnogram file
        hdr2 = {}
        assert f.tell() == 0
        assert f.read(8) == b'0       '

        # recording info
        hdr2['subject_id'] = f.read(80).decode('utf-8').strip()   # read patient info
        hdr2['recording_id'] = f.read(80).decode('utf-8').strip() # read recording date and time

        # compare the patient info and recording date of the two files
        
        if not (hdr1['subject_id'] == hdr2['subject_id'] and hdr1['recording_id'] == hdr2['recording_id']):
            print('\nPROGRAM EXIT: HYPNOGRAM FILE DOES NOT MATCH POLYSOMNOGRAPH FILE')
            import sys
            sys.exit()

        f.seek(16,1)                                              # skip records not required
        hdr2['header_n_bytes'] = int(f.read(8))                   # read bytes in header of hypnogram file    

        f.seek(hdr2['header_n_bytes'])                            # go to the end of the header info```

        data_hypno = f.read().decode('utf-8')                     # read the data
        
    time = hdr1['record_length']                    # number of secs per data record used for score period
    data_hypno_spl = data_hypno.split('\x00')
    ln = len(data_hypno_spl)
    tr = {'Sleep stage ?':-1,'Movement time':-1,'Sleep stage W':0,'Sleep stage 1':1,'Sleep stage 2':2,
      'Sleep stage 3':3,'Sleep stage 4':3,'Sleep stage R':4}
    hypno_s = []
    for i in range(ln):
        in_start = data_hypno_spl[i].find('\x15')
        if in_start == -1:
            continue
        else:
            in_stop = data_hypno_spl[i].find('\x14')
            onset = data_hypno_spl[i][1:in_start]
            duration = data_hypno_spl[i][in_start+1:in_stop]
            
            if int(onset)+int(duration) >= int(end_file):
                duration =  str(int(end_file) - int(onset))

            sleepstage = data_hypno_spl[i][in_stop+1:-1]

            nr = int(int(duration)/30)
            entry = [tr[sleepstage]]*nr
            hypno_s.extend(entry)
            
    hypno_s = np.array(hypno_s)
    sf_hyp = 1 / time
    return hypno_s, sf_hyp
            