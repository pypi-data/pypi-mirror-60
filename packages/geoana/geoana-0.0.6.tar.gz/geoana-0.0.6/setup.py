#!/usr/bin/env python
from __future__ import print_function
"""
geoana

Interactive geoscience (mostly) analytic functions.
"""

from distutils.core import setup
from setuptools import find_packages


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Scientific/Engineering :: Physics',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Operating System :: MacOS',
    'Natural Language :: English',
]

with open('README.rst') as f:
    LONG_DESCRIPTION = ''.join(f.readlines())

setup(
    name = 'geoana',
    version = '0.0.6',
    packages = find_packages(),
    install_requires = [
        'future',
        'numpy>=1.7',
        'scipy>=0.13',
        'matplotlib',
        'properties',
        'vectormath',
        'utm'
    ],
    author = 'SimPEG developers',
    author_email = 'lindseyheagy@gmail.com',
    description = 'geoana',
    long_description = LONG_DESCRIPTION,
    keywords = 'geophysics, electromagnetics',
    url = 'https://www.simpeg.xyz',
    download_url = 'https://github.com/simpeg/geoana',
    classifiers=CLASSIFIERS,
    platforms = ['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix'],
    license='MIT License',
    use_2to3 = False,
)
