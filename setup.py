#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
import pip
from pip.req import parse_requirements
from optparse import Option

__version__ = "0.2.3"


def read(fname):
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
    name='visbrain',
    version='0.1.8',
    packages=find_packages(),
    description='Hardware-accelerated data visualization for neuroscientific data in Python',
    long_description=read('README.md'),
    platforms='any',
    setup_requires=['numpy'],
    install_requires=REQS,
    dependency_links=[],
    author='Etienne Combrisson',
    maintainer='Etienne Combrisson',
    author_email='e.combrisson@gmail.com',
    url='https://github.com/EtienneCmb/visbrain',
    license=read('LICENSE'),
    include_package_data=True,
    keywords='brain MNI GPU visualization data OpenGL vispy neuroscience',
    classifiers=["Development Status :: 3 - Alpha",
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Education',
                 'Intended Audience :: Developers',
                 'Topic :: Scientific/Engineering :: Visualization',
                 "Programming Language :: Python :: 3.5"
                 ])
