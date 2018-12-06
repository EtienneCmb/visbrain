"""
Import, save and add annotations
================================

Import annotations from a text file and annotate trials.

All annotations are added to the Annotations/ tab. Then, select a row of the
table to jump to it.

Download an example of annotation file :
https://drive.google.com/file/d/0B6vtJiCQZUBvMG95RHNXbDEwaGs/view?usp=sharing

.. image:: ../../_static/examples/ex_annotations.png
"""
from visbrain.gui import Signal
from visbrain.utils import generate_eeg

sf = 512.  # sampling frequency
n_pts = 4000  # number of time points
n_trials = 125  # number of trials in the dataset

"""Generate a random EEG vector of shape (n_trials, n_pts). This time, we
smooth signals and decrease the noise on it.
"""
data, _ = generate_eeg(sf=sf, n_pts=n_pts, n_trials=n_trials, smooth=200,
                       noise=1000)

"""Specify the path to the annotation file :
"""
annotations = 'signal_annotations.txt'

Signal(data, sf=sf, axis=-1, line_lw=2., annotations=annotations).show()
