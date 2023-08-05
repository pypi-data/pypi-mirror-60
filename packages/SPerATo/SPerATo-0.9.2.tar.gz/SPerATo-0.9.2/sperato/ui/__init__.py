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

'''This module defines UserInput classes to be used by the programs 
in SPerATo.'''


from .conffile import FileConfig
from ..global_conf import (SPERATO_DEFAULT_PARAMETERS, SPERATO_CONFIG_FILE)
from .cl import (
    SPerAToListCLInput, SPerAToListHKHLRCLInput, SPerAToListPlotsCLInput
)


class UserInput:
    """Base class of all *UserInput classes with commond functionality"""
    def __init__(
            self, CLClass, argv, description,
            config_file_name=SPERATO_CONFIG_FILE
        ):
        self._command_line = CLClass(argv, description)
        self._file_config = FileConfig(config_file_name)
        self._default_conf = SPERATO_DEFAULT_PARAMETERS
        
    def __call__(self):
        self._file_config.parse()
        self._command_line()

    def __getitem__(self, item):
        value = None
        for src in (self._command_line, self._file_config, self._default_conf):
            try:
                value = src[item]
            except KeyError:
                continue
            else:
                break
        return value
    

class SPerAToListUserInput(UserInput):
    def __init__(self, argv, description):
        super().__init__(SPerAToListCLInput, argv, description)


class SPerAToListHKHLRUserInput(UserInput):
    def __init__(self, argv, description):
        super().__init__(SPerAToListHKHLRCLInput, argv, description)


class SPerAToListPlotsUserInput(UserInput):
    def __init__(self, argv, description):
        super().__init__(SPerAToListPlotsCLInput, argv, description)
