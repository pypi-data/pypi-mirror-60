#!/bin/env python

#######################################################################
#
# Copyright (C) 2020 David Palao
#
# This file is part of SPerATo.
#
#  SPerATo is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SPerATo is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SPerATo.  If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name="SPerATo",
    use_scm_version={"write_to": os.path.join("sperato", "version.py")},
    setup_requires=['setuptools_scm'],
    description="Slurm jobs Performance Analysis Tool",
    long_description=long_description,
    author="David Palao",
    author_email="palao@csc.uni-frankfurt.de",
    url="https://itp.uni-frankfurt.de/~palao/SPerATo",
    license='GNU General Public License (GPLv3)',
    packages=find_packages(),
    provides=["sperato"],
    install_requires=["numpy", "matplotlib"],
    platforms=['GNU/Linux'],
    scripts=["bin/monitoring-plots-hkhlr"],
    entry_points={'console_scripts': [
        "sperato-list = sperato.speratolist:main",
        "sperato-hkhlr = sperato.hkhlr:main",
        "sperato-plots = sperato.plots:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: System :: Monitoring",
    ],
)
