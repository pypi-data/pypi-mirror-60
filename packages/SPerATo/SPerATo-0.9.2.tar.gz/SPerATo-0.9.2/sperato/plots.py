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


"""A simple command line tool to produce plots out of data from sperato(-hkhlr)."""

import sys
import os

from .ui import SPerAToListPlotsUserInput
from .global_conf import (
    CL_JOB_STATUS_BAR_PLOT, CL_EFFICIENCY_CPU_HISTOGRAM, CL_WASTED_CPU_HISTOGRAM,
    CL_EFFICIENCY_CPU_NCPUS_2DHISTOGRAM, CL_EFFICIENCY_CPU_USED_CPUTIME_2DHISTOGRAM,
    CL_UNUSED_AND_CUMMULATIVE_CPU_HISTOGRAMS, CL_JOBS_WALLTIME_HISTOGRAM, 
)
from .aux_plots import (
    make_job_status_bar_plot, make_jobs_efficiency_histogram, make_jobs_wasted_histogram,
    make_jobs_efficiency_ncpus_histogram2D, make_jobs_efficiency_used_cputime_histogram2D,
    make_unused_and_cummulative_cpu_histogram, make_jobs_walltime_histogram, 
)
from .cluster import SPerAToListCluster
from .errors import high_level_error_wrapper


speratolist_plots_desc = __doc__


def get_input_parameters(argv):
    clinput = SPerAToListPlotsUserInput(argv, description=speratolist_plots_desc)
    clinput()
    return clinput


@high_level_error_wrapper
def main(argv=None):
    clinput = get_input_parameters(argv)
    logy = clinput["logy"]
    xbins = clinput["xbins"]
    ybins = clinput["ybins"]
    plot_type = clinput["plot_type"]
    input_file_name = clinput["indatafile"]
    cluster = SPerAToListCluster(cluster_name=clinput["cluster name"])
    date_label = clinput["add_date_label"]
    with open(input_file_name) as input_file:
        data = input_file.readlines()
    proto_plain_name = os.path.basename(input_file_name)
    plain_name = os.path.splitext(proto_plain_name)[0]
    if plot_type == CL_JOB_STATUS_BAR_PLOT:
        output_file_name = plot_type+"_"+plain_name+".png"
        title = '{cluster} usage\n({file_name})'.format(
            cluster=cluster.name,
            file_name=plain_name
        )
        make_job_status_bar_plot(data, output_file_name, title, date_label)
    elif plot_type == CL_EFFICIENCY_CPU_HISTOGRAM:
        output_file_name = plot_type+"_"+plain_name+".png"
        title = '{cluster} jobs CPU efficiency\n({file_name})'.format(
            cluster=cluster.name,
            file_name=plain_name
        )
        make_jobs_efficiency_histogram(data, output_file_name, xbins, title, date_label)
    elif plot_type == CL_WASTED_CPU_HISTOGRAM:
        output_file_name = plot_type+"_"+plain_name+".png"
        title = '{cluster} jobs wasted CPU\n({file_name})'.format(
            cluster=cluster.name,
            file_name=plain_name
        )
        make_jobs_wasted_histogram(data, output_file_name, xbins, title, date_label)
    elif plot_type == CL_EFFICIENCY_CPU_NCPUS_2DHISTOGRAM:
        output_file_name = plot_type+"_"+plain_name
        if logy:
            output_file_name += "_ylog"
        output_file_name += ".png"
        title = '{cluster}: #jobs 2D-histogram\n({file_name})'.format(
            cluster=cluster.name,
            file_name=plain_name
        )
        make_jobs_efficiency_ncpus_histogram2D(
            data, output_file_name, xbins, ybins, title, date_label, logy=logy
        )
    elif plot_type == CL_EFFICIENCY_CPU_USED_CPUTIME_2DHISTOGRAM:
        output_file_name = plot_type+"_"+plain_name
        if logy:
            output_file_name += "_ylog"
        output_file_name += ".png"
        title = '{cluster}: #jobs 2D-histogram\n({file_name})'.format(
            cluster=cluster.name,
            file_name=plain_name
        )
        make_jobs_efficiency_used_cputime_histogram2D(
            data, output_file_name, xbins, ybins, title, date_label, logy=logy
        )
    elif plot_type == CL_UNUSED_AND_CUMMULATIVE_CPU_HISTOGRAMS:
        output_file_name = plot_type+"_"+plain_name+".png"
        title = 'Unused CPU hours at {cluster}\n({file_name})'.format(
            cluster=cluster.name,
            file_name=plain_name
        )
        make_unused_and_cummulative_cpu_histogram(
            data, output_file_name, xbins, title, date_label)
    elif plot_type == CL_JOBS_WALLTIME_HISTOGRAM:
        output_file_name = plot_type+"_"+plain_name+".png"
        title = '{cluster} jobs walltime\n({file_name})'.format(
            cluster=cluster.name,
            file_name=plain_name
        )
        make_jobs_walltime_histogram(data, output_file_name, xbins, title, date_label)
