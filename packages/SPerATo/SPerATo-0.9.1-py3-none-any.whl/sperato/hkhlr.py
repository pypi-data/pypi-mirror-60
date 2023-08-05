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

"""A simple command line tool to report statistcs of interest to HKHLR
about the quality of the jobs run under slurm."""

import sys
import datetime
import calendar

from .ui import SPerAToListHKHLRUserInput
from .aux_slurm import (
    make_slurm_date, gen_jobs_in_time_interval,
    gen_preprocess_sacct_output, gen_convert_to_namedtuples, gen_filter_partition,
    gen_count_steps_and_jobs, gen_fix_missing_partition, gen_discard_sub_tasks, 
    gen_group_by_month, gen_format_hkhlr_data, gen_group_monthly_data,
    gen_remove_not_run_jobs, gen_cut_runtime_of_jobs, gen_compute_raw_data_individual_jobs,
    gen_format_data, gen_filter_data
)
from .global_conf import (
    CL_DATE_FORMAT, SLURM_STR_DATETIME, CL_HKHLR_COMMAND_MONTH_SUMMARY,
    CL_HKHLR_COMMAND_JOBS_SUMMARY,
)
from .output import SPerAToListHKHLROutputManager
from .filters import Filter
from .cluster import SPerAToListCluster, parse_partitions
from .errors import high_level_error_wrapper


speratolist_hkhlr_desc = """A command line tool to compute monthly statistics for the HKHLR 
summary plots."""

def get_input_parameters(argv):
    clinput = SPerAToListHKHLRUserInput(argv, description=speratolist_hkhlr_desc)
    clinput()
    ini_date = datetime.datetime.strptime(clinput["ini_date"], CL_DATE_FORMAT)
    one_day = datetime.timedelta(days=1)
    # + one_day: to get all jobs started in the last day of the month: see slurm.py
    end_date = datetime.datetime.strptime(clinput["end_date"], CL_DATE_FORMAT) + one_day
    return (ini_date, end_date, clinput)


@high_level_error_wrapper
def main(argv=None):
    (ini_date, end_date, clinput) = get_input_parameters(argv)
    slurm_ini_date = ini_date.strftime(SLURM_STR_DATETIME)
    slurm_end_date = end_date.strftime(SLURM_STR_DATETIME)
    command = clinput["command"]
    remote_host = clinput["host"]
    remote_user = clinput["user"]
    cluster_name = clinput["cluster name"]
    cut_low = clinput["cputime_cut_low"]
    cut_high = clinput["cputime_cut_high"]
    bar_plot = clinput["bar_plot"]
    input_file = clinput["input_data_file"]
    pre_partitions = clinput["partitions"].split(",")
    each_partition = clinput["each_partition"]
    discard_subtasks = clinput["discard_subtasks"]
    filters = [Filter(_) for _ in clinput["filter"]]
    
    cluster = SPerAToListCluster(
        hostname=remote_host, user=remote_user, cluster_name=cluster_name)
    if input_file:
        stdout = False
    else:
        stdout = True
    # Partitions:
    all_partitions = cluster.partition_names
    partitions_iterable = parse_partitions(pre_partitions, each_partition, all_partitions)
    for partitions in partitions_iterable:
        pre_partitions_for_report = ", ".join(partitions)
        if partitions == all_partitions:
            partitions_for_report = "all ({})".format(pre_partitions_for_report)
        else:
            partitions_for_report = pre_partitions_for_report
        # Body. Using generators:

        output_manager = SPerAToListHKHLROutputManager(
            cluster, bar_plot_file=bar_plot, stdout=stdout, partitions=partitions_for_report,
        )
        with output_manager as output:
            if input_file:#for plots
                with open(input_file) as f:
                    formatted_data = f.readlines()
            else:
                sacct_output = gen_jobs_in_time_interval(
                    slurm_ini_date, slurm_end_date, cluster
                )
                prepared_sacct = gen_preprocess_sacct_output(sacct_output)
                namedtuplized_sacct = gen_convert_to_namedtuples(prepared_sacct)
                if discard_subtasks:
                    relevant_sacct_lines = gen_discard_sub_tasks(namedtuplized_sacct)
                else:
                    relevant_sacct_lines = namedtuplized_sacct
                partition_fixed_data = gen_fix_missing_partition(relevant_sacct_lines)
                partition_filtered_data = gen_filter_partition(
                    partition_fixed_data, partitions
                )
                fully_filtered_data = gen_filter_data(partition_filtered_data, filters)
                if command == CL_HKHLR_COMMAND_MONTH_SUMMARY:
                    monthly_data = gen_group_by_month(
                        fully_filtered_data, ini_date, end_date
                    )
                    pre_grouped_data = gen_count_steps_and_jobs(
                        monthly_data, cut=(cut_low, cut_high)
                    )
                    final_data = gen_group_monthly_data(pre_grouped_data)
                elif command == CL_HKHLR_COMMAND_JOBS_SUMMARY:
                    cut_runtime_data = gen_cut_runtime_of_jobs(
                        fully_filtered_data, cut=(cut_low, cut_high)
                    )
                    cleaned_sacct = gen_remove_not_run_jobs(cut_runtime_data)
                    final_data = gen_compute_raw_data_individual_jobs(cleaned_sacct, cluster)
                formatted_data = gen_format_hkhlr_data(final_data)
            # Output:
            for line in formatted_data:
                output.write(line)

