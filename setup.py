#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
import pip
from pip.req import parse_requirements
from optparse import Option

__version__ = "0.3.9"
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
PACKAGE_DATA = {'visbrain.data.templates': ['B1.npz', 'B2.npz', 'B3.npz'],
                'visbrain.data.roi': ['aal.npz', 'brodmann.npz',
                                      'talairach.npz'],
                'visbrain.data.topo': ['eegref.npz'],
                'visbrain.data.icons': ['*.svg'],
                }


def read(fname):
    """Read README and LICENSE."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


options = Option('--workaround')
options.skip_requirements_regex = None
REQ_FILE = './requirements.txt'
# Hack for old pip versions: Versions greater than 1.x
# have a required parameter "sessions" in parse_requierements
if pip.__version__.startswith('1.'):
    install_reqs = parse_requirements(REQ_FILE, options=options)
else:
    from pip.download import PipSession  # pylint:disable=E0611
    options.isolated_mode = False
    install_reqs = parse_requirements(REQ_FILE,  # pylint:disable=E1123
                                      options=options,
                                      session=PipSession)

REQS = [str(ir.req) for ir in install_reqs]


setup(
    name=NAME,
    version=__version__,
    packages=find_packages(),
    package_dir={'visbrain': 'visbrain'},
    package_data=PACKAGE_DATA,
    include_package_data=True,
    description=DESCRIPTION,
    long_description=read('README.rst'),
    platforms='any',
    setup_requires=['numpy', 'pytest-runner'],
    tests_require=['pytest'],
    install_requires=REQS,
    dependency_links=[],
    author=AUTHOR,
    maintainer=MAINTAINER,
    author_email=EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    license=read('LICENSE'),
    keywords=KEYWORDS,
    classifiers=["Development Status :: 3 - Alpha",
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Education',
                 'Intended Audience :: Developers',
                 'Topic :: Scientific/Engineering :: Visualization',
                 "Programming Language :: Python :: 3.5"
                 ],
    entry_points='''
        [console_scripts]
        visbrain_sleep=visbrain.cli:cli_sleep
        visbrain_fig_hyp=visbrain.cli:cli_fig_hyp
        visbrain_sleep_stats=visbrain.cli:cli_sleep_stats
    ''')
