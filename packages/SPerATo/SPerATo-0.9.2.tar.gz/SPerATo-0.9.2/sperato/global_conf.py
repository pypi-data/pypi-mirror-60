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

import time
import logging
import datetime
import os
import socket


CL_DEF_NUM_ITEMS_OUTPUT = 10

CL_RESOURCE_CPU = "CPU"
CL_RESOURCE_TYPES = [CL_RESOURCE_CPU]
CL_DEF_RESOURCE_TYPE = CL_RESOURCE_CPU

CL_OUTPUT_CATEGORIES = ["User", "Account"]
CL_DEF_OUTPUT_CATEGORY = "User"

CL_DEFAULT_PARTITIONS = "all"
CL_DEFAULT_EACH_PARTITION = False

CL_OUTPUT_ORDERS = ["lowest", "highest"]
CL_DEF_OUTPUT_ORDER = CL_OUTPUT_ORDERS[1]

CL_OUTPUT_SORT_PARAMS = [
    "NCPUs", "wasted_CPU", "available_CPU", "global_efficiency_CPU", 
    "efficiency_CPU"
    ]#, "RAM_ratio"]
CL_DEF_OUTPUT_SORT_PARAM = CL_OUTPUT_SORT_PARAMS[1]

CL_OUTPUT_PARAM_NAMES = [
    "median(NCPUs)", "Wasted CPU [c*h]", "Avail CPU [c*h]", "global eff. CPU", 
    "mean(Efficiency CPU)"
    ]#, "median(RAM used/req)"]

CL_DEF_INITIAL_TIME_IN_DAYS = 7
CL_DEF_END_TIME_SsE = time.time()
_now = datetime.datetime.now()
CL_DEF_INI_DATE_STATISTICS = datetime.datetime(_now.year, _now.month, 1)
CL_DEF_END_DATE_STATISTICS = _now
CL_DATE_FORMAT = "%Y/%m/%d"
SLURM_STR_DATETIME = "%Y-%m-%dT%H:%M:%S"
SACCT_COMMAND = "sacct"
SCONTROL_COMMAND = "scontrol"

CL_HKHLR_COMMAND_MONTH_SUMMARY = "month"
CL_HKHLR_COMMAND_JOBS_SUMMARY = "jobs"
CL_HKHLR_COMMANDS = (CL_HKHLR_COMMAND_MONTH_SUMMARY, CL_HKHLR_COMMAND_JOBS_SUMMARY)

# The next must be something that identifies uniquely the output lines:
OUTPUT_COL_SEPARATOR = " | "

CL_DEF_RAM_UPPER_BOUND = None
CL_DEF_RAM_LOWER_BOUND = None

# Correct the double count that slurm does of cores with hyper threading:
CORRECT_DOUBLE_CPU_COUNT = True

CL_DEFAULT_DUMP_PERFORMANCE_DATA = False

CL_JOB_STATUS_BAR_PLOT = "job-status-bar-plot"
CL_EFFICIENCY_CPU_HISTOGRAM = "efficiency-cpu-histogram"
CL_WASTED_CPU_HISTOGRAM = "wasted-cpu-histogram"
CL_UNUSED_AND_CUMMULATIVE_CPU_HISTOGRAMS = "unused-and-cummulative-cpu-histogram"
CL_EFFICIENCY_CPU_NCPUS_2DHISTOGRAM = "efficiency-cpu-ncpus-2Dhistogram"
CL_EFFICIENCY_CPU_USED_CPUTIME_2DHISTOGRAM = "efficiency-cpu-used-cputime-2Dhistogram"
CL_JOBS_WALLTIME_HISTOGRAM = "jobs-walltime-histogram"
CL_VALID_PLOT_TYPES = (
    CL_JOB_STATUS_BAR_PLOT, CL_EFFICIENCY_CPU_HISTOGRAM, CL_WASTED_CPU_HISTOGRAM,
    CL_EFFICIENCY_CPU_NCPUS_2DHISTOGRAM, CL_EFFICIENCY_CPU_USED_CPUTIME_2DHISTOGRAM,
    CL_UNUSED_AND_CUMMULATIVE_CPU_HISTOGRAMS, CL_JOBS_WALLTIME_HISTOGRAM,
)
CL_VALID_PLOT_TYPES_STR = ", ".join(CL_VALID_PLOT_TYPES)
CL_DEFAULT_ADD_DATE_LABEL = False
SPERATOLIST_MONTH_FORMAT = "{year}/{month:02}"
CL_DEFAULT_DISCARD_SUBTASKS = False

CL_DEFAULT_LOGY = False
CL_DEF_XBINS = 100
CL_DEF_YBINS = 100

#  Next is critical: it must be the same as the value contained in the init
# script:
SPERATO_CONF_ENVIRON_VAR = "SPERATO_CONF"
SPERATOD_PIDFILE_VAR="SPERATOD_PIDFILE"

SPERATO_CONFIG_FILE = os.path.expanduser("~/.sperato.conf")

DEF_REMOTE_HOST = socket.gethostname()
DEF_REMOTE_USER = "root"
DEF_CLUSTER_NAME = "unknown cluster"

# The next dict is to be able to make homogeneous attribute fetching in
# sperato.cl.UserInput.__getitem__
SPERATO_DEFAULT_PARAMETERS = {
    "host": DEF_REMOTE_HOST,
    "user": DEF_REMOTE_USER,
    "cluster name": DEF_CLUSTER_NAME,
}
