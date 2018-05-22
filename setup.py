#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup

__version__ = "0.4.0"
NAME = 'visbrain'
AUTHOR = "Visbrain developpers"
MAINTAINER = "Etienne Combrisson"
EMAIL = 'e.combrisson@gmail.com'
KEYWORDS = "brain MNI GPU visualization data OpenGL vispy neuroscience " + \
           "sleep data-mining"
DESCRIPTION = "Hardware-accelerated visualization suite for " + \
              "brain-data in Python"
URL = 'http://visbrain.org/'
DOWNLOAD_URL = "https://github.com/EtienneCmb/visbrain/archive/" + \
               "v" + __version__ + ".tar.gz"
# Data path :
HERE = os.path.abspath(os.path.dirname(__file__))
PACKAGE_DATA = {'visbrain.data.templates': ['B1.npz', 'B2.npz', 'B3.npz'],
                'visbrain.data.roi': ['aal.npz', 'brodmann.npz',
                                      'talairach.npz'],
                'visbrain.data.topo': ['eegref.npz'],
                'visbrain.data.icons': ['*.svg'],
                }


def read(fname):
    """Read README and LICENSE."""
    return open(os.path.join(HERE, fname), 'rb').read().decode('utf8')


setup(
    # DESCRIPTION
    name=NAME,
    version=__version__,
    description=DESCRIPTION,
    long_description=read('README.rst'),
    keywords=KEYWORDS,
    license=read('LICENSE'),
    author=AUTHOR,
    maintainer=MAINTAINER,
    author_email=EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    # PACKAGE / DATA
    packages=['visbrain'],
    package_dir={'visbrain': 'visbrain'},
    package_data=PACKAGE_DATA,
    include_package_data=True,
    platforms='any',
    setup_requires=['numpy'],
    install_requires=[
        "numpy>=1.13",
        "scipy",
        "vispy>=0.5.2",
        "matplotlib>=1.5.5",
        "pyqt5",
        "pillow",
        "Click"
    ],
    dependency_links=[],
    classifiers=["Development Status :: 3 - Alpha",
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Education',
                 'Intended Audience :: Developers',
                 'Topic :: Scientific/Engineering :: Visualization',
                 "Programming Language :: Python :: 3 :: Only",
                 "Programming Language :: Python :: 3.5",
                 "Operating System :: MacOS",
                 "Operating System :: POSIX :: Linux",
                 "Operating System :: Microsoft :: Windows",
                 "Natural Language :: English"
                 ],
    entry_points='''
        [console_scripts]
        visbrain_sleep=visbrain.cli:cli_sleep
        visbrain_fig_hyp=visbrain.cli:cli_fig_hyp
        visbrain_sleep_stats=visbrain.cli:cli_sleep_stats
    ''')
