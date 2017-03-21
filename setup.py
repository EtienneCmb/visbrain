#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='visbrain',
    version='0.1.6',
    packages=find_packages(),
    description='Hardware-accelerated data visualization for neuroscientific data in Python',
    long_description=read('README.md'),
    install_requires=[
        'numpy',
        'scipy',
        'pillow',
        'matplotlib<=1.5.1',
        'pyopengl',
        'vispy',
    ],
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
