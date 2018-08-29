"""
Get sleep statistics
====================

Get sleep statictics such as sleep stages duration, duration of the hypnogram.
"""
from visbrain.io import download_file, get_sleep_stats

###############################################################################
# Hypnogram data
###############################################################################
# Download a hypnogram example

path_to_hypno = download_file("s101_jbe.hyp", astype='example_data')

###############################################################################
# Get sleep statistics
###############################################################################
# Sleep statistics are going to be printed in the terminal and then saved in a
# `my_stats.csv`

get_sleep_stats(path_to_hypno, output_file='my_stats.csv')
