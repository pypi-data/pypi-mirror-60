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

"""In this module an interface to the cluster is defined."""

import socket
import subprocess as sp
from .slurm import SPerAToListSlurm


class SPerAToListCluster:
    def __init__(self, user=None, hostname="", cluster_name=""):
        self.hostname = hostname
        self.name = cluster_name
        self.unqualified_hostname = hostname.split(".")[0]
        self.user = user
        self.local_hostname = socket.gethostname()
        self._set_pre_command()
        self.slurm = SPerAToListSlurm(self)
        
    def _set_pre_command(self):
        self.precmd = ()
        if self.is_remote:
            user_host = self.hostname
            if self.user:
                user_host = self.user+"@"+user_host
            self.precmd = ("ssh", user_host)

    @property
    def is_remote(self):
        if not hasattr(self, "_is_remote"):
            if self.local_hostname in (self.hostname, self.unqualified_hostname) :
                self._is_remote = False
            else:
                self._is_remote = True
        return self._is_remote

    @property
    def is_local(self):
        return not self.is_remote
    
    def run(self, cmd):
        """It runs the cmd on the cluster (remotely or locally), depending on the hostname
        """
        cmd = list(self.precmd) + list(cmd)
        cmd_result = sp.Popen(cmd, stdout=sp.PIPE)
        cmd_output = cmd_result.stdout
        return cmd_output

    @property
    def partitions(self):
        return self.slurm.partitions

    @property
    def partition_names(self):
        return self.slurm.partition_names
    
    @property
    def nodes(self):
        return self.slurm.nodes

    @property
    def node_names(self):
        return self.slurm.node_names
    


def parse_partitions(pre_partitions, each_partition, all_partitions):
    proto_partitions = set()
    partitions_iterable = []
    multi_partition_report = False
    if each_partition is True:
        multi_partition_report = True
    for partition in pre_partitions:
        if partition == "all":
            for part in all_partitions:
                proto_partitions.add(part)
        elif partition in all_partitions:
            proto_partitions.add(partition)
    proto_partitions = list(proto_partitions)
    proto_partitions.sort()
    partitions_iterable.append(proto_partitions)
    if multi_partition_report:
        for partition in proto_partitions:
            partitions_iterable.append([partition])
    return partitions_iterable
