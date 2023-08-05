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

"""Some error handling..."""

import sys
import traceback
from functools import wraps


def high_level_error_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e, file=sys.stderr)
            return -1
    return wrapper

            
class SPerAToListWarning(UserWarning):
    def __init__(self, message, original_error=None, debug=False):
        self._original_error = original_error
        self._debug = debug
        self._pre_message = "   --- "
        self._post_message = " ---"
        self.make_message(message)

    def make_message(self, message):
        self._message = "{}{}{}".format(self._pre_message, message, self._post_message)
        if self._original_error:
            self._message += "\n"+" "*len(self._pre_message)+str(self._original_error)
    
    def __str__(self):
        msg = self._message
        if self._debug and self._original_error:
            addons = traceback.format_exception(*sys.exc_info())
            msg += "\n=>".join(addons)
        return msg

    def print_me(self):
        print(self, file=sys.stderr)


class SPerAToListMalformedSacctLine(SPerAToListWarning):
    def __init__(self, line, original_error=None):
        self._line = line
        super().__init__("Malformed sacct line: skipped", original_error)











