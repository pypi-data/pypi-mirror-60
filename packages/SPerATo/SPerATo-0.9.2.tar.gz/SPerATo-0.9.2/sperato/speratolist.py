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

"""A simple command line tool to report about the quality of the jobs 
run under slurm."""

import sys

from .ui import SPerAToListUserInput
from .aux_slurm import (
    make_slurm_date, gen_jobs_in_time_interval,
    gen_preprocess_sacct_output, gen_convert_to_namedtuples, 
    gen_take_job_summaries, gen_remove_not_run_jobs, gen_compute_raw_data,
    gen_format_for_data_dump, gen_discard_sub_tasks, 
    gen_filter_partition, gen_analyze_data, gen_format_data, gen_cut_data,
    gen_group_data, gen_sort_data, gen_filter_data, gen_fix_missing_partition,
)
from .global_conf import (
    CL_OUTPUT_ORDERS, CL_DEF_OUTPUT_ORDER, CL_OUTPUT_SORT_PARAMS,
    CL_DEF_OUTPUT_SORT_PARAM, CL_OUTPUT_CATEGORIES
)
from .output import SPerAToListOutputManager
from .filters import Filter
from .cluster import SPerAToListCluster, parse_partitions
from .errors import high_level_error_wrapper


speratolist_desc = """A command line tool to show a list with worst/best usage 
cases in the latest given days."""

def get_input_parameters(argv):
    clinput = SPerAToListUserInput(argv, description=speratolist_desc)
    clinput()
    tN = clinput["end_time"]
    days = clinput["initial_time_delta_days"]
    t_end = make_slurm_date(tN)
    t0 = tN - 24*60*60*float(days)
    t_ini = make_slurm_date(t0)
    order = clinput["output_order"]
    if not order in CL_OUTPUT_ORDERS:
        order = CL_DEF_OUTPUT_ORDER
    sort_param = clinput["sorted_by"]
    if not sort_param in CL_OUTPUT_SORT_PARAMS:
        sort_param = CL_DEF_OUTPUT_SORT_PARAM
    proto_categories = clinput["output_category"].split(",")
    categories = []
    for cat in proto_categories:
        if cat in CL_OUTPUT_CATEGORIES:
            categories.append(cat)
        else:
            print("Wrong category: {0}".format(cat), file=sys.stderr)
    attach_filename = clinput["attached_csv"]
    if attach_filename:
        attach_filename = "{0}_{1}".format(clinput["attached_csv"], 
            output_category)
    filters = [Filter(_) for _ in clinput["filter"]]
    return (
        t_ini, t_end, days, order, sort_param, categories, attach_filename, filters,
        clinput,
    )


@high_level_error_wrapper
def main(argv=None):
    (t_ini, t_end, days, order, sort_param, categories, attach_filename, filters,
     clinput) = get_input_parameters(argv)
    remote_host = clinput["host"]
    remote_user = clinput["user"]
    cluster_name = clinput["cluster name"]
    nitems = clinput["nitems"]
    second_sort_param = clinput["after_cut_sort_by"]
    second_sort_order = clinput["second_sort_order"]
    pre_partitions = clinput["partitions"].split(",")
    each_partition = clinput["each_partition"]
    dump_performance_data_and_exit = clinput["dump_performance_data"]
    discard_subtasks = clinput["discard_subtasks"]
    cluster = SPerAToListCluster(
        hostname=remote_host, user=remote_user, cluster_name=cluster_name
    )
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
        for output_category in categories:
            output_manager = SPerAToListOutputManager(emails=clinput["email_to"], 
                stdout=clinput["stdout"], emails_attach_csv=attach_filename, 
                category=output_category, resource=clinput["resource_type"], 
                t_ini=t_ini, t_end=clinput["end_time"], nitems=nitems, order=order, 
                days=days, sort_param=sort_param, filters=filters,
                partitions=partitions_for_report, dump_data=dump_performance_data_and_exit,
                cluster=cluster
            )
            with output_manager as output:
                sacct_output = gen_jobs_in_time_interval(t_ini, t_end, cluster)
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
                summarized_jobs = gen_take_job_summaries(partition_filtered_data)
                cleaned_sacct = gen_remove_not_run_jobs(summarized_jobs)
                performance_data = gen_compute_raw_data(cleaned_sacct, cluster)
                if dump_performance_data_and_exit:
                    formatted_data = gen_format_for_data_dump(performance_data)
                else:
                    groupped_data = gen_group_data(performance_data, output_category)
                    analyzed_data = gen_analyze_data(groupped_data, output_category)
                    filtered_data = gen_filter_data(analyzed_data, filters)
                    sorted_data = gen_sort_data(filtered_data, sort_param, order)
                    cut_data = gen_cut_data(sorted_data, cut=nitems)
                    if second_sort_param:
                        final_data = gen_sort_data(cut_data, 
                            second_sort_param, second_sort_order)
                    else:
                        final_data = cut_data
                    formatted_data = gen_format_data(final_data, output_category, 
                        nitems, order, sort_param, days)
                # Output:
                for line in formatted_data:
                    output.write(line)

