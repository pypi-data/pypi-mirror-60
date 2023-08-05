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

"""In this module, generators and coroutines are named with "gen_" and 
"co_" prefixes, respectively.
"""

import sys
import subprocess as sp
import time
from collections import namedtuple
from itertools import groupby, tee
from statistics import mean, median_low, StatisticsError
import socket
import datetime

from .global_conf import (
    CL_OUTPUT_SORT_PARAMS, CL_OUTPUT_PARAM_NAMES, OUTPUT_COL_SEPARATOR,
    SCONTROL_COMMAND, SLURM_STR_DATETIME, CORRECT_DOUBLE_CPU_COUNT, SPERATOLIST_MONTH_FORMAT,
)
from .errors import (SPerAToListWarning, SPerAToListMalformedSacctLine)


# Some constants:
memory_factors = {"M": 1., "G": 1024., "K": 0.0009765625, "T": 1048576.}
memory_units_to_G = {
    "M": 0.0009765625, "G": 1., "K": 9.5367431640625e-07, "T": 1024.
}
minutes_to_seconds = 60
hours_to_seconds = minutes_to_seconds*minutes_to_seconds
seconds_to_hours = 1/hours_to_seconds
days_to_seconds = hours_to_seconds*24
output_str = {k:v for k, v in zip(CL_OUTPUT_SORT_PARAMS, CL_OUTPUT_PARAM_NAMES)}
output_str["njobs"] = "#jobs"
_SUMMARY_JOB_ORDER = ["JobID", "User", "Account"] + CL_OUTPUT_SORT_PARAMS + ["Partition"]
_SUMMARY_INDIVIDUAL_JOBS_ORDER = [
    "user_identifier", "job_id", "job_wall_time", "job_cpu_time", "job_wall_coretime",
    "job_resource_utilization_efficiency", "job_resource_unused", "allocated_resources_cores",
    "job_state", "job_type",
]
wasted_cpu_str = CL_OUTPUT_SORT_PARAMS[1]
avail_cpu_str = CL_OUTPUT_SORT_PARAMS[2]
ncpus_str = CL_OUTPUT_SORT_PARAMS[0]
glob_eff_cpu_str = CL_OUTPUT_SORT_PARAMS[3]
eff_cpu_str = CL_OUTPUT_SORT_PARAMS[4]
#ram_ratio_str = CL_OUTPUT_SORT_PARAMS[5]
njobs_str = "njobs"
output_order = [
    wasted_cpu_str, avail_cpu_str, njobs_str, ncpus_str, glob_eff_cpu_str, eff_cpu_str
]#, ram_ratio_str]
_OUTPUT_FORMATS = [
    "{0:<15}", "{0:>{1}.1f}", "{0:>{1}.1f}", "{0:>{1}d}", "{0:>{1}d}", 
    "{0:>{1}.5f}", "{0:>{1}.5f}"
]#, "{0:>{1}.5f}"]
_TITLE_OUTPUT_FORMATS = [
    "{0:<15}", "{0:>{1}}", "{0:>{1}}", "{0:>{1}}", "{0:>{1}}", 
    "{0:>{1}}", "{0:>{1}}"
]#, "{0:>{1}}"]
    
def make_slurm_date(time_in_seconds=None):
    t = time.localtime(time_in_seconds)
    return time.strftime(SLURM_STR_DATETIME, t)

def scontrol_output_to_dict(scontrol_output):
    scontrol_dict = {}
    for line in scontrol_output:
        try:
            line_str = line.decode()
        except AttributeError:
            #I assume that it is a str:
            line_str = line
        finally:
            line_str = line_str.strip()
        if line_str == "":
            continue
        if line_str.count("=") == 1:
            # sometimes in this case scontrol show node uses a one line option to
            # include spaces in the value
            key, value = line_str.strip().split("=")
            scontrol_dict[key] = value
        else:
            for option in line_str.split(" "):
                #  There are two cases:
                #   1) 'CPUAlloc=80 CPUTot=80 CPULoad=26.60'
                # and things like 
                #   2) 'AllocTRES=cpu=80,mem=80000M'
                # The second argument of split works in both cases:
                key, value = option.strip().split("=", 1)
                scontrol_dict[key] = value
    return scontrol_dict

def gen_jobs_in_time_interval(start, end, cluster):
    slurm_out = cluster.slurm.get_all_jobs_in_time_interval(start, end)
    for line in slurm_out.readlines():
        yield line

def gen_preprocess_sacct_output(lines):
    for line in lines:
        try:
            yield line.decode().strip().split("|")
        except UnicodeDecodeError as e:
            #need to create a SPerAToListError or something
            print(f"[{e}] {line}", file=sys.stderr)

def gen_convert_to_namedtuples(lines):
    line = next(lines)
    Record = namedtuple("SacctRecord", line)
    for line in lines:
        try:
            r = Record(*line)
        except TypeError as e:
            SPerAToListMalformedSacctLine(line=line, original_error=e).print_me()
        else:
            yield r

def gen_discard_sub_tasks(records):
    for record in records:
        jobid = record.JobID
        canonical_jobid = get_jobid(record)
        if jobid == canonical_jobid:
            yield record
            
def gen_fix_missing_partition(records):
    """Slurm does not assign partition names to sub-jobs (steps or batches).
    That causes problems when it comes to analyzing job steps.
    This generator fixes that 'problem'.
    """
    job2partition_map = {}
    #missing = set()
    for record in records:
        if record.Partition == "":
            jobid = get_jobid(record)
            try:
                partition = job2partition_map[jobid]
            except KeyError as e:
                #missing.append(jobid)
                if jobid == record.JobID:
                    # in this case, the 
                    SPerAToListWarning(
                        "Wrong record (record: {}): empty partition".format(record),
                        original_error=e
                    ).print_me()
                    partition = ""
            finally:
                record = record._replace(Partition=partition)
        else:
            jobid = get_jobid(record)
            job2partition_map[jobid] = record.Partition
            #if jobid in missing:
            #    record._replace(Partition=job2partition_map[jobid])
            #    missing.remove(jobid)
        yield record
        
def gen_filter_partition(records, partitions):
    for record in records:
        partition = record.Partition
        if partition in partitions:
            yield record
    
def get_jobid(record):
    proto_jobid = record.JobID
    if "." in proto_jobid:
        jobid = proto_jobid[:proto_jobid.find(".")]
    else:
        jobid = proto_jobid
    return jobid

def mem2M(val):
    """Given a memory value returned by sacct, like 
    '', '23K', '100M' or '2G', '3'
    it returns a string containing that value in units of M. In the examples
    '0' '0' '100' '2048' '0'
    If no valid units are found, 0 is returned.
    """
    if val in ("", "0"):
        res = "0"
    else:
        newval, units = val[:-1], val[-1]
        if units in memory_factors.keys():
            newval = float(newval)
            res = str(round(newval*memory_factors[units]))
        else:
            res = "0"
    return res

def get_month_end(record):
    slurm_end = record.End
    date = datetime.datetime.strptime(slurm_end, SLURM_STR_DATETIME)
    return date

def gen_group_by_month(records, ini_date, end_date):
    for date, unique_monthly_records in groupby(records, get_month_end):
        if date >= ini_date and date <= end_date:
            month = SPERATOLIST_MONTH_FORMAT.format(year=date.year, month=date.month)
            yield (month, unique_monthly_records)

def apply_cputime_cut(record, cut_seconds):
    if cut_seconds is None:
        result = True
    else:
        cut_low_s, cut_high_s = cut_seconds
        cputime = float(record.CPUTimeRAW)
        if cut_low_s is None or cputime >= cut_low_s:
            low_result = True
        else:
            low_result = False
        if cut_high_s is None or cputime <= cut_high_s:
            high_result = True
        else:
            high_result = False
        result = low_result and high_result
    return result

def convert_cut_to_seconds(cut):
    if cut is None:
        result = cut
    else:
        if cut.endswith("d"):
            unit_factor = days_to_seconds
            tail_slice = -1
        elif cut.endswith("m"):
            unit_factor = minutes_to_seconds
            tail_slice = -1
        elif cut.endswith("h"):
            unit_factor = hours_to_seconds
            tail_slice = -1
        elif cut.endswith("s"):
            unit_factor = 1
            tail_slice = -1
        else:
            unit_factor = 1
            tail_slice = None
        result = float(cut[:tail_slice])*unit_factor
    return result

def get_cut_tuple(cut):
    if cut:
        cut_low, cut_high = cut
        cut_low_s = convert_cut_to_seconds(cut_low)
        cut_high_s = convert_cut_to_seconds(cut_high)
        cut = cut_low_s, cut_high_s
    return cut

def gen_count_steps_and_jobs(data, cut=None):
    cut = get_cut_tuple(cut)
    users = {}
    accounts = {}

    for item in data:
        month, records = item
        total_tasks = 0
        tasks_completed = 0
        jobs_completed = 0
        tasks_failed = 0
        tasks_timeout = 0
        tasks_cancelled = 0
        tasks_other = 0
        for jobid, unique_jobid_records in groupby(records, get_jobid):
            steps = [_ for _ in unique_jobid_records if apply_cputime_cut(_, cut)]
            how_many = len(steps)
            total_tasks += how_many
            for job in steps:
                if job.State in ("COMPLETED", ):
                    tasks_completed += 1
                    if job.JobID == jobid:
                        # this is the job itself
                        jobs_completed += 1
                elif job.State in ("FAILED", "NODE_FAIL"):
                    tasks_failed += 1
                    user = job.User
                    if user in users:
                        users[user] += 1
                    else:
                        users[user] = 0
                    account = job.Account
                    if account in accounts:
                        accounts[account] += 1
                    else:
                        accounts[account] = 0
                elif job.State in ("TIMEOUT", ):
                    tasks_timeout += 1
                elif job.State in ("CANCELLED", "DEADLINE"):
                    tasks_cancelled += 1
                else:
                    tasks_other += 1
        yield (month, total_tasks, tasks_completed, jobs_completed, tasks_failed, tasks_timeout,
               tasks_cancelled)#, tasks_other)

def gen_group_monthly_data(data):
    final = {}
    for element in data:
        (month, *rest) = element
        if month in final.keys():
            for i, _ in enumerate(rest):
                final[month][i] += _
        else:
            final[month] = list(rest)
    sorted_data = [(month, values) for (month, values) in final.items()]
    sorted_data.sort()
    for month, values in sorted_data:
        yield (month,) +tuple(values)
            
def gen_format_hkhlr_data(data):
    head = [k for k in _SUMMARY_INDIVIDUAL_JOBS_ORDER]
    head[0] = "#"+head[0]
    yield " ".join(head)
    for item in data:
        yield " ".join(str(_) for _ in item)
                
def gen_take_job_summaries(records):
    for jobid, unique_jobid_records in groupby(records, get_jobid):
        first = next(unique_jobid_records)
        all_AveRSS = [mem2M(first.AveRSS)]
        for i in unique_jobid_records:
            AveRSS = mem2M(i.AveRSS)
            all_AveRSS.append(AveRSS)
        first = first._replace(AveRSS=str(max(all_AveRSS)))
        yield first

def gen_cut_runtime_of_jobs(records, cut=None):
    cut = get_cut_tuple(cut)
    for r in records:
        if apply_cputime_cut(r, cut):
            yield r
        else:
            pass

def gen_remove_not_run_jobs(records):
    for r in records:
        if r.CPUTimeRAW == "0":
                pass
        else:
            yield r

def str_to_float(x):
    # Sometimes the slurm numbers are 00.3, which are not valid literals 
    # for base-10:
    while True:
        if x.startswith("0") and len(x) > 1:
            x = x[1:]
        else:
            break
    try:
        res = float(x)
    except ValueError:
        print(f"It is not possible to convert '{x}' to float", file=sys.stderr)
        raise
    return res
    
def str_time_to_seconds(t):
    t_parts = t.split("-")
    if len(t_parts) == 2:
        days = int(t_parts[0])
    else:
        days = 0
    sp_parts = [str_to_float(_) for _ in t_parts[-1].split(":")]
    num_colons = len(sp_parts)
    if num_colons == 3:
        h, m, s = sp_parts
    elif num_colons == 2:
        h = 0.
        m, s = sp_parts
    elif num_colons == 1:
        h = 0.0
        m = 0.0
        s = sp_parts[0]
    else:
        raise ValueError("no way to parse:",t)
    value = (((days*24)+h)*minutes_to_seconds+m)*minutes_to_seconds+s
    return value

def str_time_to_datetime(t):
    return datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S")

# def old_compute_wasted_CPU_ch(record):
#     used = str_time_to_seconds(record.TotalCPU)
#     avail = float(record.CPUTimeRAW)
#     wasted = (avail-used)*seconds_to_hours
#     return wasted

def compute_wasted_CPU_seconds(record, avail_hours, ncpus):
    return compute_wasted_CPU_ch(record, avail_hours, ncpus)*hours_to_seconds
    
def compute_wasted_CPU_ch(record, avail_hours, ncpus):
    used = str_time_to_seconds(record.TotalCPU)
    used_corrected= used*ncpus/int(record.NCPUS)
    wasted = avail_hours-used_corrected*seconds_to_hours
    return wasted

def compute_walltime_seconds(record):
    start = str_time_to_datetime(record.Start)
    end = str_time_to_datetime(record.End)
    return (end-start).total_seconds()
    # The next way should be equivalent, but the parsing of the time is more difficult:
    #elapsed = str_time_to_datetime(record.Elapsed)
    #return elapsed.total_seconds()

def compute_avail_CPU_ch(record, ncpus):
    avail = compute_walltime_seconds(record)*ncpus
    if ncpus == int(record.NCPUS):
        avail2 = float(record.CPUTimeRAW)
        pre_ass_msg = "computed available cpu time(={}) and slurm value(={}) don't match"
        ass_msg = pre_ass_msg.format(avail, avail2)
        if avail != avail2:
            SPerAToListWarning(ass_msg).print_me()
    avail_hours = avail*seconds_to_hours
    return avail_hours

def compute_eff_CPU(record, avail_hours, ncpus):
    used = str_time_to_seconds(record.TotalCPU)
    used_corrected= used*ncpus/int(record.NCPUS)
    avail = avail_hours*hours_to_seconds
    return (used_corrected/avail)

def compute_RAM_ratio(record):
    reqmem = record.ReqMem
    core_node = reqmem[-1]
    if core_node == "c":
        a = int(record.NCPUS)
    elif core_node == "n":
        a = int(record.NNodes)
    units = reqmem[-2]
    if units in ("M", "G", "T", "K"):
        b = memory_factors[units]
    else:
        b = 0
    if a == 0 or b == 0:
        req_ram = 0
    else:
        cn_less = reqmem.strip("c").strip("n")
        memory = float(cn_less.strip("M").strip("G").strip("K").strip("T"))
        req_ram = memory*a*b
    if req_ram == 0:
        return None
    used_ram = float(record.AveRSS)*float(record.NCPUS)
    return used_ram/req_ram

def compute_RAM_per_core(record):
    maxram = record.MaxRSS
    units = maxram[-1]
    if units in memory_units_to_G.keys():
        b = memory_units_to_G[units]
    else:
        b = 1
    memory = float(maxram.strip("M").strip("G").strip("K").strip("T"))
    memory = memory*b
    ram_per_core = memory/float(record.NCPUS)
    return ram_per_core

def old_get_slurm_nodes_from_NodeList(node_list, host):
    cmd = [SCONTROL_COMMAND, "show", "hostname", node_list]
    slurm = run_on_cluster(cmd, host)
    nodes = [_.decode().strip() for _ in slurm.readlines()]
    return nodes

def find_relevant_commas(node_list):
    comma_positions = []
    searching_main_comma = True
    for index, element in enumerate(node_list):
        if searching_main_comma:
            if element == ",":
                comma_positions.append(index)
                continue
            if element == "[":
                searching_main_comma = False
        else:
            if element == "]":
                searching_main_comma = True
    return comma_positions

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def get_host_groups_from_node_list(node_list, main_commas):
    host_groups = []
    indices = [-1] + main_commas + [len(node_list)]
    for idx0, idx1 in pairwise(indices):
        host_groups.append(node_list[idx0+1:idx1])
    return host_groups

def expand_nodes_group(group):
    ini_idx = group.find("[")
    if ini_idx == -1:
        nodes = [group]
    else:
        nodes = []
        end_idx = group.find("]")
        prefix = group[:ini_idx]
        sub_groups = group[ini_idx+1:end_idx].split(",")
        for sub_group in sub_groups:
            if "-" in sub_group:
                start_sub, end_sub = sub_group.split("-")
                num_chars = len(start_sub)
                assert num_chars == len(end_sub), "oh, oh...: problems parsing"+sub_group
                nums = list(range(int(start_sub), int(end_sub)+1))
                for num in nums:
                    f = "{"+":0{}".format(num_chars)+"}"
                    nodes.append(prefix+f.format(num))
            else:
                nodes.append(prefix+sub_group)
    return nodes

def get_slurm_nodes_from_NodeList(node_list):#, cluster):
    # first pass: split groups
    main_commas = find_relevant_commas(node_list)
    host_groups = get_host_groups_from_node_list(node_list, main_commas)
    # second pass: expand groups
    nodes = []
    for group in host_groups:
        nodes.extend(expand_nodes_group(group))
    return nodes
    
def compute_ncpus(r, cluster):
    """The record 'r' should contain the number of cpus that the job is requested
    to work with. BUT this might be wrong if the nodes are not shared and a user
    requests less cpus than the node has.
    In this functions that deficiency is corrected."""
    #is_exclusive = is_slurm_partition_exclusive(r.Partition, host)
    is_exclusive = cluster.slurm.is_partition_exclusive(r.Partition)
    if is_exclusive:
        nodes = get_slurm_nodes_from_NodeList(r.NodeList)
        if CORRECT_DOUBLE_CPU_COUNT:
            # Horrible hack, I know. It corrects the fact that slurm lies concerning the number
            # of cores in Intel nodes:
            cpus = []
            for node in nodes:
                cpu_count = int(cluster.nodes[node]["CPUTot"])
                #if cluster.nodes[node]["loewe_intel_node"]:
                #    cpu_count /= 2
                try:
                    hyper_threading_factor = int(cluster.nodes[node]["ThreadsPerCore"])
                except (KeyError, ValueError):
                    hyper_threading_factor = 1
                cpus.append(cpu_count/hyper_threading_factor)
        else:
            cpus = [int(cluster.nodes[node]["CPUTot"]) for node in nodes]
        ncpus = sum(cpus)
    else:
        ncpus = r.NCPUS
    return int(ncpus)

def gen_compute_raw_data_individual_jobs(records, cluster):
    for r in records:
        if r.State in ("FAILED", "COMPLETED", "TIMEOUT"):
            try:
                if r.State == "FAILED":
                    state = "F"
                elif r.State == "COMPLETED":
                    state = "C"
                elif r.State == "TIMEOUT":
                    state = "T"
                ncpus = compute_ncpus(r, cluster)
                walltime_seconds = compute_walltime_seconds(r)
                avail_hours = compute_avail_CPU_ch(r, ncpus)
                avail_seconds = avail_hours*hours_to_seconds
                wasted_seconds = compute_wasted_CPU_seconds(r, avail_hours, ncpus)
                used_seconds = avail_seconds-wasted_seconds
                for positive_thing in (avail_seconds, wasted_seconds,
                        used_seconds, walltime_seconds):
                    if positive_thing < 0:
                        raise ValueError
                jobtype = "T" if "." in r.JobID else "J"
                resd = {
                    "job_id": r.JobID,
                    "user_identifier": r.Account,
                    "job_wall_time": walltime_seconds,
                    "job_cpu_time": used_seconds,
                    "job_wall_coretime": walltime_seconds*ncpus,
                    "job_resource_utilization_efficiency": 100*compute_eff_CPU(r, avail_hours, ncpus),
                    "job_resource_unused": wasted_seconds,
                    "allocated_resources_cores": ncpus,
                    "job_state": state,
                    "job_type": jobtype,
                }
                res = [resd[k] for k in _SUMMARY_INDIVIDUAL_JOBS_ORDER]
            except Exception as e:
                try:
                    jobid = r.JobID
                except AttributeError:
                    jobid = "?"
                SPerAToListWarning(
                    f"Wrong record ({r}) [jobid: {jobid}]: skipped",
                    original_error=e
                ).print_me()
            else:
                yield res
        
def gen_compute_raw_data(records, cluster):
    for r in records:
        try:
            ncpus = compute_ncpus(r, cluster)
            avail_hours = compute_avail_CPU_ch(r, ncpus)
            resd = {
                "JobID": r.JobID, "User": r.User, "Account": r.Account,
                "Partition":r.Partition,
                "NCPUs": ncpus, "wasted_CPU": compute_wasted_CPU_ch(r, avail_hours, ncpus), 
                "available_CPU": avail_hours, 
                "efficiency_CPU": compute_eff_CPU(r, avail_hours, ncpus),
                #"RAM_per_core": compute_RAM_per_core(r),
            }#, "RAM_ratio": compute_RAM_ratio(r)}
            resd["global_efficiency_CPU"] = 0
            res = [resd[k] for k in _SUMMARY_JOB_ORDER]
        except Exception as e:
            try:
                jobid = r.JobID
            except AttributeError:
                jobid = "?"
            SPerAToListWarning(
                f"Wrong record ({r}) [jobid: {jobid}]: skipped",
                original_error=e, debug=True
            ).print_me()
        else:
            yield res

def old_gen_filter_partition(raw_data, partitions):
    for job in raw_data:
        partition = job[-1]
        if partition in partitions:
            yield job
    
def gen_format_for_data_dump(data):
    yield "# "+" ".join(_SUMMARY_JOB_ORDER)
    for record in data:
        yield " ".join([str(_) for _ in record])
        
def get_category_key_from_job(field_name, record):
    if field_name == "User":
        return record[1]
    elif field_name == "Account":
        return record[2]
    elif field_name == "Partition":
        return record[-1]
    else:
        raise TypeError("{0}: not a valid field name".format(field_name))

def gen_group_data(job_items, field_name):
    grouped_dict = {}
    for job in job_items:
        key = get_category_key_from_job(field_name, job)
        if key in grouped_dict:
            grouped_dict[key].append(job)
        else:
            grouped_dict[key] = [job]
    for key, value in grouped_dict.items():
        yield key,value
            
def gen_analyze_data(data_items, group_param):
    # fix the issue with indices below:
    # add another dict: for k in _SUMMARY_JOB_ORDER: funcs[k](item)
    all_njobs = 0
    all_ncpus = []
    all_wasted_cpu = []
    all_avail_cpu = []
    all_eff_cpu = []
    for key, job_list in data_items:
        njobs = 0
        ncpus = []
        wasted_cpu = []
        avail_cpu = []
        eff_cpu = []
        #ram_ratio = []
        for job in job_list:
            njobs += 1
            all_njobs += 1
            ncpus.append(job[3])
            all_ncpus.append(job[3])
            wasted_cpu.append(job[4])
            all_wasted_cpu.append(job[4])
            avail_cpu.append(job[5])
            all_avail_cpu.append(job[5])
            eff_cpu.append(job[7])
            all_eff_cpu.append(job[7])
        if njobs == 0:
            continue
        res = {"global": False}
        #res[group_param] = key
        res["User"] = job[1]
        res["Account"] = job[2]
        res[njobs_str] = njobs
        res[wasted_cpu_str] = sum(wasted_cpu)
        res[avail_cpu_str] = sum(avail_cpu)
        res[ncpus_str] = median_low(ncpus)
        res[glob_eff_cpu_str] = 1-res[wasted_cpu_str]/res[avail_cpu_str]
        res[eff_cpu_str] = mean(eff_cpu)
        yield res
    res = {"global": True}
    #res[group_param] = "all jobs"
    res["User"] = "all jobs"
    res["Account"] = "all jobs"
    res[njobs_str] = all_njobs
    res[wasted_cpu_str] = sum(all_wasted_cpu)
    res[avail_cpu_str] = sum(all_avail_cpu)
    try:
        median_ncpus = median_low(all_ncpus)
    except StatisticsError:
        median_ncpus = 0
    finally:
        res[ncpus_str] = median_ncpus
    try:
        global_eff_cpu = 1-res[wasted_cpu_str]/res[avail_cpu_str]
    except ZeroDivisionError:
        global_eff_cpu = 0
    finally:
        res[glob_eff_cpu_str] = global_eff_cpu
    try:
        mean_eff_cpu = mean(all_eff_cpu)
    except StatisticsError:
        mean_eff_cpu = 0
    finally:
        res[eff_cpu_str] = mean_eff_cpu
    yield res

def gen_filter_data(items, filters=()):
    """It can filter namedtuple (added) instances and dictionaries (original)."""
    for item in items:
        try:
            if item["global"]:
                yield item
        except TypeError:
            pass
        for item_filter in filters:
            item_pass_filter = item_filter(item)
            if not item_pass_filter:
                break
        else:
            yield item

def gen_sort_data(data_items, sort_param, order):
    if order.lower() == "lowest":
        rev = False
    else:
        rev = True
    raw_items = []
    for item in data_items:
        if item["global"]:
            yield item
        else:
            raw_items.append(item)
    #raw_items = list(data_items)
    sorted_items = sorted(raw_items, key=lambda x: x[sort_param], reverse=rev)
    for new_item in sorted_items:
        yield new_item

def gen_cut_data(data, cut):
    count = 0
    try:
        for item in data:
            if item["global"]:
                global_item = item
            else:
                yield item
                count += 1
            if count == cut:
                raise StopIteration
    finally:
        yield global_item
    
def gen_format_data(records, group_param, n, order, sort_param, days):
    sep = OUTPUT_COL_SEPARATOR
    out_keys = [group_param]+output_order
    out_list = [group_param]+[output_str[k] for k in output_order]
    len_out_list = [len(i) for i in out_list]
    line = sep.join([f.format(i,l) for f,i,l in zip(_TITLE_OUTPUT_FORMATS, out_list, len_out_list)])
    len_line = len(line)
    yield line
    yield "="*len_line
    for r in records:
        if r["global"]:
            yield ""#to separate the global info from the group
        yield sep.join([
            f.format(r[i],l) for f,i,l in zip(_OUTPUT_FORMATS, out_keys, len_out_list)
        ])
    yield ""#to end with a new line
        
