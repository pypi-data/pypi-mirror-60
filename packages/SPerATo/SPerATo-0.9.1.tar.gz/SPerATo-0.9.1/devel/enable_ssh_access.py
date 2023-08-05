#!/bin/env python3.6

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


"""Script that adds a ssh key to the authorized_keys file
"""

import sys
import argparse
import os
from glob import iglob, glob
import shutil


DEFAULT_AUTHORIZED_FILE = os.path.expanduser("~/.ssh/authorized_keys")


def parse_conf():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'pub_key', metavar='PUB-KEY', 
        help='public key to add to the authorized list'
    )
    parser.add_argument(
        "-a", '--authorized-file', dest='authorized', metavar="AUTHORIZED FILE",
        default=DEFAULT_AUTHORIZED_FILE, help='authorized file where the key will be installed')
    parser.add_argument(
        "-X", '--self-destroy', dest='boom', action='count',
        default=-1, help='self destroy script and public key')

    args = parser.parse_args()
    return args


def main():
    conf = parse_conf()
    self = sys.argv[0]
    # get access and modification times of authorized file::
    statinfo = os.stat(conf.authorized)
    times = (statinfo.st_atime, statinfo.st_mtime)
    # read key:
    with open(conf.pub_key) as pub_key_file:
        pub_key = pub_key_file.read()
    # write key to authorized file:
    with open(conf.authorized, "a") as au:
        au.write(pub_key)
        au.write("\n")
    # set back access and modification time of authorized:
    os.utime(conf.authorized, times=times)
    # destroy key and self?
    if conf.boom == 0:
        print(f"File '{conf.pub_key}' would be removed with one more '-X'")
        print(f"File '{self}' would be removed with one more '-X'")
    elif conf.boom >= 1:
        os.unlink(conf.pub_key)
        print(f"File '{conf.pub_key}' removed")
        os.unlink(self)
        print(f"File '{self}' removed")


        
if __name__ == "__main__":
    sys.exit(main())
