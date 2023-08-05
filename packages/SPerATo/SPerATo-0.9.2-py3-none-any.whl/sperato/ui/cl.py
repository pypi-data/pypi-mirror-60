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
import argparse
from ..global_conf import (
    CL_DEF_NUM_ITEMS_OUTPUT, CL_RESOURCE_TYPES, CL_DEF_RESOURCE_TYPE,
    CL_DEF_OUTPUT_CATEGORY, CL_OUTPUT_CATEGORIES, CL_DEF_OUTPUT_ORDER, CL_OUTPUT_ORDERS,
    CL_DEF_OUTPUT_SORT_PARAM, CL_OUTPUT_SORT_PARAMS,
    CL_DEF_INITIAL_TIME_IN_DAYS, CL_DEF_END_TIME_SsE,
    CL_DEF_INI_DATE_STATISTICS, CL_DEF_END_DATE_STATISTICS, CL_DATE_FORMAT, 
    CL_DEF_RAM_UPPER_BOUND, CL_DEF_RAM_LOWER_BOUND,
    DEF_REMOTE_HOST, DEF_REMOTE_USER, DEF_CLUSTER_NAME, CL_DEFAULT_PARTITIONS,
    CL_DEFAULT_EACH_PARTITION, CL_DEFAULT_DUMP_PERFORMANCE_DATA, CL_VALID_PLOT_TYPES_STR,
    CL_DEFAULT_ADD_DATE_LABEL, CL_DEFAULT_DISCARD_SUBTASKS, CL_DEFAULT_LOGY,
    CL_DEF_XBINS, CL_DEF_YBINS, 
)
from .. import __version__


class BaseSPerAToListCLInput:
    """A class to encompass the input through the command line. This base class
    provides common functionality to SPerAToListCLInput and SPerAToListHKHLRCLInput."""
    def __init__(self, argv=None, description=""):
        if argv is None:
            argv = sys.argv[1:]
        self.argv = argv
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            '--version', action='version',
            version='%(prog)s {}'.format(__version__)
        )
        self._parser = parser
        self.define_arguments()
        self.choose_arguments()
        self.add_arguments()
        
    def __call__(self):
        self.args = self._parser.parse_args(self.argv)
        self.set_global_conf()
        self._args_dict = vars(self.args)

    def __getitem__(self, key):
        return self._args_dict[key]
        
    def set_global_conf(self):
        # Example of usage:
        # config_file_name = os.path.expanduser(self.args.global_conf)
        # self._full_global_conf = configparser.ConfigParser()
        # self._full_global_conf.read(config_file_name)
        pass

    def define_arguments(self):
        self.possible_arguments = {}

        host_help = "ssh remote host (DEFAULT: conf file -> {})".format(
            DEF_REMOTE_HOST
        )
        self.possible_arguments["-H", "--remote-host"] = dict(
            default=argparse.SUPPRESS, dest="host", help=host_help,
        )

        user_help = "ssh remote user (DEFAULT: conf file -> {})".format(
            DEF_REMOTE_USER
        )
        self.possible_arguments["-u", "--remote-user"] = dict(
            default=argparse.SUPPRESS, dest="user", help=user_help,
        )

        name_help = "name of cluster (DEFAULT: conf file -> {})".format(
            DEF_CLUSTER_NAME
        )
        self.possible_arguments["-N", "--cluster-name"] = dict(
            default=argparse.SUPPRESS, dest="cluster name", help=name_help,
        )

        partitions_help = "comma sep. list of partition names; a special value"\
            + " 'all' is allowed, meaning all partitions together"\
            + " (DEFAULT: %(default)s)"
        self.possible_arguments["-P", "--partitions"] = dict(
            default=CL_DEFAULT_PARTITIONS, dest="partitions", help=partitions_help,
        )

        each_partition_help = "Want an individual report for each given partition?"
        self.possible_arguments["-E", "--each-partition"] = dict(
            default=CL_DEFAULT_EACH_PARTITION, dest="each_partition", help=each_partition_help,
            action="store_true",
        )

        num_items_help = "number of items in output (DEFAULT: %(default)s)"
        self.possible_arguments["-n", "--num-items"] = dict( 
            default=CL_DEF_NUM_ITEMS_OUTPUT, dest="nitems", type=int, help=num_items_help,
        )

        cat_help = "comma sep. list; possible values: "\
            + ", ".join(CL_OUTPUT_CATEGORIES) + " (DEFAULT: %(default)s)"
        self.possible_arguments["-c", "--category"] = dict(
            default=CL_DEF_OUTPUT_CATEGORY, dest="output_category", help=cat_help,
        )

        resource_help = "Type of resource to report about. Possible values "\
            "are: " + ", ".join(CL_RESOURCE_TYPES) + " (DEFAULT: %(default)s)"
        self.possible_arguments["-r", "--resource-type"] = dict( 
            default=CL_DEF_RESOURCE_TYPE, dest="resource_type", help=resource_help,
        )

        order_help = "possible orders: "+", ".join(CL_OUTPUT_ORDERS)\
            + " (DEFAULT: %(default)s)"
        self.possible_arguments["-o", "--output-order"] = dict(
            default=CL_DEF_OUTPUT_ORDER, dest="output_order", help=order_help,
        )

        second_order_help = "order for optional second sort after cut. "\
            "Possible orders: " + ", ".join(CL_OUTPUT_ORDERS)\
            + " (DEFAULT: %(default)s)"
        self.possible_arguments[("--order-after-second-cut",)] = dict( 
            default=CL_DEF_OUTPUT_ORDER, dest="second_sort_order", help=second_order_help,
        )

        sorted_help = "possible values: "+", ".join(CL_OUTPUT_SORT_PARAMS)\
            + " (DEFAULT: %(default)s)"
        self.possible_arguments["-s", "--sorted-by"] = dict( 
            default=CL_DEF_OUTPUT_SORT_PARAM, dest="sorted_by", help=sorted_help,
        )

        second_sort_help = "optional second sort after cut. Possible values: "\
            + ", ".join(CL_OUTPUT_SORT_PARAMS)
        self.possible_arguments[("--sort-after-cut-by",)] = dict(
            default=None, dest="after_cut_sort_by", help=second_sort_help
        )

        self.possible_arguments["-e", "--send-email-to"] = dict(
            default=None, dest="email_to",
            help="comma sep. list of addresses to send the output to"
        )

        filter_help = "[Account|User]:comma sep. list. For example: "\
          "'-f Account:staff,frankfurt' to display only info about accounts "\
          "'frankfurt' and 'staff'. This option can be given many times. "\
          "Values within each filter are or-ed; but different filters are "\
          "and-ed. For example: with '-f Account:staff -f User:user1,user2'"\
          " one gets info from jobs run with account 'staff' by either 'user1'"\
          " or 'user2'."
        self.possible_arguments["-f", "--filter"] = dict(
            default=[], action="append", dest="filter", help=filter_help,
        )

        time_metavar = "DAYS"
        time_help="the initial time of the list in days is t_end-{0}"\
            " (DEFAULT: %(default)s)".format(time_metavar)
        self.possible_arguments["-t", "--initial-time"] = dict( 
            default=CL_DEF_INITIAL_TIME_IN_DAYS, dest="initial_time_delta_days",
            metavar=time_metavar, help=time_help,
        )

        end_time_metavar = "SECONDS_SINCE_EPOCH"
        end_time_help="the end time of the list in seconds since the Epoch"\
            " (DEFAULT: NOW [=%(default).2f])"
        self.possible_arguments["-T", "--end-time"] = dict(
            default=CL_DEF_END_TIME_SsE, dest="end_time", metavar=end_time_metavar,
            help=end_time_help, type=float
        )

        no_stdout_help="supress standard output"
        self.possible_arguments["-X", "--supress-stdout"] = dict(
            dest="stdout", action="store_false", help=no_stdout_help,
        )

        attach_help = "file name's prefix of output csv file to be attached "\
            "by email"
        self.possible_arguments[("--attach-csv-file-to-email",)] = dict(
            default=False, dest="attached_csv", help=attach_help,
        )

        ram_meta = "GB"
        ram_upper_help = "only jobs with ram/core <= %(metavar)s are "\
          "considered (DISABLED)"
        self.possible_arguments[("--ram-upper-bound",)] = dict( 
            default=CL_DEF_RAM_UPPER_BOUND, dest="ram_upper_bound", help=ram_upper_help,
            metavar=ram_meta,
        )
        
        ram_lower_help = "only jobs with ram/core >= %(metavar)s are "\
          "considered (DISABLED)"
        self.possible_arguments[("--ram-lower-bound",)] = dict( 
            default=CL_DEF_RAM_LOWER_BOUND, dest="ram_lower_bound", help=ram_lower_help,
            metavar=ram_meta,
        )

        dump_performance_data_help = "Simply dump the performance data, before any anlysis, "\
          "and exit"
        self.possible_arguments["-d", "--dump-performance-data"] = dict(
            default=CL_DEFAULT_DUMP_PERFORMANCE_DATA, dest="dump_performance_data",
            help=dump_performance_data_help, action="store_true", 
        )

        command_help = "valid entries: 'month' to get monthly statistics; "\
          "'jobs' to get a summary of all jobs in a period"
        self.possible_arguments[("command",)] = dict(help=command_help)

        date_metavar = "YYYY/MM/DD"
        def_ini_date = CL_DEF_INI_DATE_STATISTICS.strftime(CL_DATE_FORMAT)
        ini_date_help="the initial date for the statistics (included)"\
            " (DEFAULT: beginning of the current month [=%(default)s])"
        self.possible_arguments["-t", "--initial-date"] = dict(
            default=def_ini_date, dest="ini_date", metavar=date_metavar, help=ini_date_help,
        )

        def_end_date = CL_DEF_END_DATE_STATISTICS.strftime(CL_DATE_FORMAT)
        end_date_help="the end date for the statistics (included)"\
            " (DEFAULT: now [=%(default)s])"
        self.possible_arguments["-T", "--end-date"] = dict(
            default=def_end_date, dest="end_date", metavar=date_metavar, help=end_date_help,
        )

        cut_low_help = "[month command] only include jobs/steps with more cpu time than"\
            + " indicated (DEFAULT: %(default)s)"
        self.possible_arguments["-c", "--cputime-higher-than"] = dict( 
            default=None, dest="cputime_cut_low", help=cut_low_help,
        )

        cut_high_help = "[month command] only include jobs/steps with less cpu time than"\
            + " indicated (DEFAULT: %(default)s)"
        self.possible_arguments["-C", "--cputime-lower-than"] = dict( 
            default=None, dest="cputime_cut_high", help=cut_high_help,
        )
        
        self.possible_arguments["-b", "--produce-bar-plot"] = dict(
            default=None, dest="bar_plot",
            help="name of file for bar plot with overal global statistics of jobs",
        )

        data_from_file_help = "".join((
            "Do not collect data from the cluster, instead, take from a file; useful to produce ",
            "plots from already produced data."))
        self.possible_arguments["-F", "--data-from-file"] = dict(
            default=None, dest="input_data_file", help=data_from_file_help,
        )
        
        plottype_help = "type of plot to be produced; valid types are: "
        plottype_help += "{plot_types}".format(plot_types=CL_VALID_PLOT_TYPES_STR)
        self.possible_arguments[("plot_type",)] = dict(help=plottype_help)

        indatafile_help = "mandatory input data file"
        self.possible_arguments[("indatafile",)] = dict(help=indatafile_help)

        add_date_label_help = "Want a label with the time when the plot was done in it?"
        self.possible_arguments["-L", "--add-date-label"] = dict(
            default=CL_DEFAULT_ADD_DATE_LABEL, dest="add_date_label", help=add_date_label_help,
            action="store_true",
        )

        discard_subtasks_help = "Want to produce data related only to slurm jobs, and not to"\
          " any sub-task?"
        self.possible_arguments["-j", "--discard-subtasks-data"] = dict(
            default=CL_DEFAULT_DISCARD_SUBTASKS, dest="discard_subtasks",
            help=discard_subtasks_help, action="store_true",
        )

        logy_help = "Want log scale in y axis?"
        self.possible_arguments[("--y-log-scale",)] = dict(
            default=CL_DEFAULT_LOGY, dest="logy", help=logy_help,
            action="store_true",
        )

        xbins_help = "(for histograms) number of bins in X direction (default: %(default)s)"
        self.possible_arguments[("--histogram-bins-X",)] = dict( 
            default=CL_DEF_XBINS, dest="xbins", help=xbins_help, type=int,
        )

        ybins_help = "(for histograms) number of bins in Y direction (default: %(default)s)"
        self.possible_arguments[("--histogram-bins-Y",)] = dict( 
            default=CL_DEF_YBINS, dest="ybins", help=ybins_help, type=int,
        )

    def add_arguments(self):
        for key in self.arguments:
            values = self.possible_arguments[key]
            self._parser.add_argument(*key, **values)
            
    def choose_arguments(self):
        """This is the method that must be overloaded by subclasses to add the wished options."""
        pass
    

class SPerAToListCLInput(BaseSPerAToListCLInput):
    def choose_arguments(self):
        self.arguments = (
            ("-u", "--remote-user"), ("-H", "--remote-host"), ("-N", "--cluster-name"),
            ("-P", "--partitions"),
            ("-E", "--each-partition"), ("-n", "--num-items"), ("-c", "--category"),
            ("-r", "--resource-type"), ("-o", "--output-order"), ("--order-after-second-cut", ),
            ("-s", "--sorted-by"), ("--sort-after-cut-by",), ("-e", "--send-email-to"),
            ("-f", "--filter"), ("-t", "--initial-time"), ("-T", "--end-time"),
            ("-X", "--supress-stdout"), ("--attach-csv-file-to-email",), ("--ram-upper-bound",),
            ("--ram-lower-bound",), ("-d", "--dump-performance-data"),
            ("-j", "--discard-subtasks-data"),
        )

        
class SPerAToListHKHLRCLInput(BaseSPerAToListCLInput):
    def choose_arguments(self):
        self.arguments = (
            ("command",),
            ("-u", "--remote-user"), ("-H", "--remote-host"), ("-N", "--cluster-name"),
            ("-P", "--partitions"),
            ("-E", "--each-partition"), ("-t", "--initial-date"), ("-T", "--end-date"),
            ("-c", "--cputime-higher-than"), ("-C", "--cputime-lower-than"),
            ("-b", "--produce-bar-plot"), ("-F", "--data-from-file"),
            ("-j", "--discard-subtasks-data"), ("-f", "--filter"), 
        )


class SPerAToListPlotsCLInput(BaseSPerAToListCLInput):
    def choose_arguments(self):
        self.arguments = (
            ("plot_type",), ("indatafile",), ("-N", "--cluster-name"),
            ("-L", "--add-date-label"), ("--y-log-scale",), 
            ("--histogram-bins-X",), ("--histogram-bins-Y",), 
        )
    
        
