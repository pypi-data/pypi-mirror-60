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

"""This module defines a SPerAToListSlurm object that serves as an interface to
slurm.
"""

from .global_conf import SACCT_COMMAND, SCONTROL_COMMAND
from .aux_slurm import scontrol_output_to_dict


class SPerAToListSlurm:
    def __init__(self, cluster):
        self.cluster = cluster

    def scontrol_show(self, entity_input, entity_output):
        cmd = [SCONTROL_COMMAND, "show", entity_input]
        slurm_out = self.cluster.run(cmd)
        entities = {}
        for line in slurm_out.readlines():
            line_str = line.decode()
            if entity_output in line_str:
                entity, *rest = line_str.split()
                entity_name = entity.strip().split("=")[1]
                entities[entity_name] = {"raw_info": [" ".join(rest)]}
            elif line_str.strip() != "":
                entities[entity_name]["raw_info"].append(line_str)
        for entity_name in entities.keys():
            raw_info = entities[entity_name]["raw_info"]
            scontrol_dict = scontrol_output_to_dict(raw_info)
            for key, value in scontrol_dict.items():
                entities[entity_name][key] = value
        return entities

    @property
    def partition_names(self):
        names = list(self.partitions.keys())
        names.sort()
        return names
    
    @property
    def partitions(self):
        if not hasattr(self, "_partitions"):
            partitions = self.scontrol_show("partition", "PartitionName")
            self._partitions = partitions
        return self._partitions
    
    def is_partition_exclusive(self, partition_name):
        is_exclusive = False
        shared = self.partitions[partition_name].get("Shared", "")
        oversubscribe = self.partitions[partition_name].get("OverSubscribe", "")
        if "exclusive" in (shared.lower(), oversubscribe.lower()):
            is_exclusive = True
        return is_exclusive

    def get_all_jobs_in_time_interval(self, ini, end):
        cmd = [
            SACCT_COMMAND, "-s", "ca,cd,dl,f,nf,pr,to", "-P", "-o", "ALL",
            "-S", ini, "-E", end
        ]
        return self.cluster.run(cmd)

    @property
    def node_names(self):
        names = list(self.nodes.keys())
        names.sort()
        return names
    
    @property
    def nodes(self):
        if not hasattr(self, "_nodes"):
            nodes = self.scontrol_show("node", "NodeName")
            self._nodes = nodes
            # for node in self._nodes:
            #     if node.startswith("intel"):
            #         is_intel_node = True
            #     else:
            #         is_intel_node = False
            #     self._nodes[node]["loewe_intel_node"] = is_intel_node
        return self._nodes
    
