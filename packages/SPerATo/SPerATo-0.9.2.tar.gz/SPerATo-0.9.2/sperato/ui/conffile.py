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

import configparser


class FileConfig:
    SECTION = "SPerATo"
    
    def __init__(self, file_name):
        self._config_file = file_name
        
    def parse(self):
        conf = configparser.ConfigParser()
        try:
            conf.read(self._config_file)
        except TypeError:
            pass
        self._conf = conf

    def __getitem__(self, item):
        return self._conf[self.SECTION][item]
