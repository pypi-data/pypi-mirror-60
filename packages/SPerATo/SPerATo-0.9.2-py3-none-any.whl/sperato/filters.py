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

"""Filters for items managed by sperato-list."""

class FilterError(Exception):
    pass


class Filter:
    def __init__(self, raw_filter):
        category, value = raw_filter.split(":")
        self.category = category
        self.values = value.split(",")

    def __call__(self, item):
        value_found = False
        try:
            value_in_item = self._get_data_from_item(item)
        except FilterError:
            pass
        else:
            if value_in_item in self.values:
                value_found = True
        return value_found

    def _get_data_from_item(self, item):
        try:
            value = item[self.category]
        except (KeyError, TypeError):
            try:
                value = getattr(item, self.category)
            except AttributeError:
                raise FilterError
        return value
    
    def __str__(self):
        s = "filter: '{0}' one of '{1}'".format(self.category, self.values)
        return s
