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


import sys
import os
import csv

from .email import SPerAToListEmail
from .global_conf import (
    OUTPUT_COL_SEPARATOR, CL_DEF_END_TIME_SsE, CL_DEF_NUM_ITEMS_OUTPUT,
    CL_DEF_OUTPUT_ORDER, CL_DEF_OUTPUT_SORT_PARAM, CL_DEF_INITIAL_TIME_IN_DAYS
)
from .aux_slurm import make_slurm_date
from .cluster import SPerAToListCluster


class BaseOutputManager:
    def __init__(self):
        self._targets = []
        self.make_header()
        
    def make_header(self):
        self.header = ""
        
    def __enter__(self):
        self.write(self.header)
        return self

    def write(self, line):
        for t in self._targets:
            t.write(line)

    def __exit__(self, exc_ty, exc_val, tb):
        for t in self._targets:
            t.close()


class SPerAToListHKHLROutputManager(BaseOutputManager):
    def __init__(self, cluster, bar_plot_file=None, stdout=True, partitions=None):
        self.partitions = partitions
        super().__init__()
        if stdout:
            self._targets.append(SPerAToListSTDOutput())
        if bar_plot_file:
            self._targets.append(SPerAToListHKHLRMonthBarPlotOutput(cluster, bar_plot_file))

    def make_header(self):
        self.header = "# partitions = {}".format(self.partitions)

        
class SPerAToListOutputManager(BaseOutputManager):
    """A class to manage the possible different outputs of speratolist."""
    def __init__(
            self, emails=None, stdout=None, emails_attach_csv=False,
            category="", resource="", t_ini=None, t_end=None,
            nitems=CL_DEF_NUM_ITEMS_OUTPUT, order=CL_DEF_OUTPUT_ORDER,
            sort_param=CL_DEF_OUTPUT_SORT_PARAM,
            days=CL_DEF_INITIAL_TIME_IN_DAYS,
            cluster=None,
            filters=None, partitions=None, dump_data=False):
        self._t_ini = t_ini
        self._t_end = t_end
        self._category = category
        self._resource = resource
        self._nitems = nitems
        self._order = order
        self._sort_param = sort_param
        self._days= days
        self._filters = filters
        self._partitions = partitions
        self._dump_data = dump_data
        if self._dump_data:
            self._header_prefix = "#"
        else:
            self._header_prefix = ""
        if not cluster:
            cluster = SPerAToListCluster()
        self._cluster = cluster
        super().__init__()
        self.make_email_subject()
        if emails:
            email = SPerAToListEmailOutput(emails, self.email_subject,\
                                        attach_csv=emails_attach_csv)
            self._targets.append(email)
        if stdout:
            self._targets.append(SPerAToListSTDOutput())
        
    def make_header(self):
        now_str = str(CL_DEF_END_TIME_SsE)
        t_end_str = str(self._t_end)
        if self._dump_data:
            res = ""
        else:
            res = "\nSummary of {nitems} {category}s at {cluster.name} with {order} "\
                "{sort_param}"
            if now_str == t_end_str:
                res += " in the latest {days} days"
            res += " with:\n"
        if self._filters:
            for item_filter in self._filters:
                res += "{prefix}  [{0}]\n".format(
                    str(item_filter), prefix=self._header_prefix
                )
        res += "{prefix}  [initial time: {t_ini}]\n"
        res += "{prefix}  [final time:   {t_end}]\n"
        res += "{prefix}  [partitions: {partitions}]\n"
        self.header = res.format(
            nitems=self._nitems, category=self._category, order=self._order,
            sort_param=self._sort_param, days=self._days, t_ini=self._t_ini,
            t_end=make_slurm_date(self._t_end), partitions=self._partitions,
            prefix=self._header_prefix, cluster=self._cluster
        )

    def make_email_subject(self):
        s = "[{cluster.name}][SPerATo] -- report of {resource} performance: {category} {partitions}"
        if self._partitions.startswith("all"):
            partitions_msg = ""
        else:
            partitions_msg = " (partitions: {})".format(self._partitions)
        self.email_subject = s.format(
            resource=self._resource, category=self._category, partitions=partitions_msg,
            cluster=self._cluster
        )


class SPerAToListOutput:
    """Base abstract class of the hierarchy."""
    def __init__(self, underlying):
        self._under = underlying

    def write(self, line):
        self._under.write(line)
        
    def close(self):
        pass


class SPerAToListSTDOutput(SPerAToListOutput):
    def __init__(self):
        self._under = sys.stdout

    def write(self, line):
        print(line, file=sys.stdout)

    def close(self):
        self._under.flush()
        

class SPerAToListEmailOutput(SPerAToListOutput):
    def __init__(self, to, subject, attach_csv=False):
        self._under = SPerAToListEmail(to, subject)
        if attach_csv:
            self.attached_csv = os.path.basename(attach_csv) + ".csv"
            self._csv_fname = os.path.join("/tmp", self.attached_csv)
            self._csvf = open(self._csv_fname, "w")
            self._csv = csv.writer(self._csvf)
        else:
            self.attached_csv = attach_csv

    def write(self, line):
        self._under.feed(line)
        if self.attached_csv:
            if OUTPUT_COL_SEPARATOR in line:
                #this tells the line is data and not a header or something:
                els = [e.strip() for e in line.split(OUTPUT_COL_SEPARATOR)]
                self._csv.writerow(els)
                
    def close(self):
        if self.attached_csv:
            self._csvf.close()
            self._under.attach(self._csv_fname, attached_name=self.attached_csv)
            os.unlink(self._csv_fname)
        self._under.send()


class SPerAToListHKHLRMonthBarPlotOutput(SPerAToListOutput):
    def __init__(self, cluster, bar_plot_file):
        self.cluster = cluster
        self.bar_plot_file = bar_plot_file
        super().__init__([])

    def write(self, line):
        self._under.append(line.split())

    def _sanitize_data(self):
        data = [_ for _ in self._under if len(_)>0]
        self._under = data
        
    def close(self):
        make_job_status_bar_plot()
