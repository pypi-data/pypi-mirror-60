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

"""A collection of functions for plotting called from speratolist-plots"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.patches as patches
import matplotlib.path as path

import time


def sanitize_monthly_data(data):
    new_data = []
    for line in data:
        line_stripped = line.strip()
        if len(line_stripped) > 0:
            if not line_stripped.startswith("#"):
                new_data.append(line_stripped)
    return new_data

def make_job_status_bar_plot(lines, output_file_name, title=None, date_label=False):
    lines = sanitize_monthly_data(lines)
    lines = [_.split() for _ in lines]
    N = len(lines)
    completed = [int(_[2].strip()) for _ in lines]
    fails = [int(_[4].strip()) for _ in lines]
    timeout = [int(_[5].strip()) for _ in lines]
    cancelled = [int(_[6].strip()) for _ in lines]
    #other = [int(_[7].strip()) for _ in lines]

    completed_timeout = [x+y for x,y in zip(completed, timeout)]
    completed_timeout_fails = [x+y for x,y in zip(completed_timeout, fails)]
    completed_timeout_fails_cancelled = [
        x+y for x,y in zip(completed_timeout_fails, cancelled)
    ]

    #maximum = max(
    #    [x+y+z+i+j for x,y,z,i,j in zip(completed, fails, timeout, cancelled, other)]
    #)
    maximum = max(
        [x+y+z+i for x,y,z,i in zip(completed, fails, timeout, cancelled)]
    )
    delta_max = round(maximum/10, -3)
    maximum = round(maximum+delta_max, -3)
    months = [_[0] for _ in lines]
    ind = np.arange(N)    # the x locations for the groups
    width = 0.5       # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, completed, width, color='g')
    p2 = plt.bar(ind, timeout, width, color='b', bottom=completed)
    p3 = plt.bar(ind, fails, width, color='r', bottom=completed_timeout)
    p4 = plt.bar(ind, cancelled, width, color='y', bottom=completed_timeout_fails)
    #p5 = plt.bar(ind, other, width, color='m', bottom=completed_timeout_fails_cancelled)
    plt.ylabel('Number of jobs')
    plt.xlabel('Month')
    plt.title(title)
    plt.xticks(ind-width/2., months, rotation=30)
    if delta_max > 0:
        plt.yticks(np.arange(0, maximum, delta_max))
    plt.legend(
        (p1[0], p2[0], p3[0], p4[0],
         #p5[0],
        ),
        ('completed', "timeout", 'failed', "cancelled",
         #"other",
        )
    )
    if date_label:
        plt.text(
            ind[-1]+2, 0.05, "{}".format(time.asctime()),
            color="gray",
            ha="right", va="bottom",
            alpha=0.5,
            rotation="vertical",
        )
    plt.savefig(output_file_name, dpi=200)
    #plt.show()

def make_jobs_efficiency_histogram(
        lines, output_file_name, xbins, title=None, date_label=False):
    lines = sanitize_monthly_data(lines)
    lines = [_.split() for _ in lines]
    #take only jobs:
    data = [_ for _ in lines if not "." in _[1]]
    N = len(data)
    hist_data = [float(_[5].strip()) for _ in data]
    n, bins, patches = plt.hist(hist_data, xbins, facecolor='green', alpha=0.75)
    axes = plt.gca()
    axes.set_xlim([0, 100])
    plt.ylabel('Number of jobs')
    plt.xlabel('Efficiency (100*used/avail)')
    plt.title(title)

    if date_label:
        plt.text(
            bins[-1]*1.1, 0.05, "{}".format(time.asctime()),
            color="gray",
            ha="right", va="bottom",
            alpha=0.5,
            rotation="vertical",
        )
    plt.savefig(output_file_name, dpi=200)
    #plt.show()

def make_jobs_wasted_histogram(lines, output_file_name, xbins, title=None, date_label=False):
    lines = sanitize_monthly_data(lines)
    lines = [_.split() for _ in lines]
    #take only jobs:
    data = [_ for _ in lines if not "." in _[1]]
    N = len(data)
    hist_data = [1-float(_[5].strip())/100 for _ in data]
    n, bins, patches = plt.hist(hist_data, xbins, facecolor='orange', alpha=0.75)
    plt.ylabel('Number of jobs')
    plt.xlabel('(wasted/avail) CPU time')
    plt.title(title)

    if date_label:
        plt.text(
            bins[-1]*1.1, 0.05, "{}".format(time.asctime()),
            color="gray",
            ha="right", va="bottom",
            alpha=0.5,
            rotation="vertical",
        )
    plt.savefig(output_file_name, dpi=200)
    #plt.show()


def make_jobs_efficiency_ncpus_histogram2D(
        lines, output_file_name, xbins, ybins, title=None, date_label=False, logy=False):
    lines = sanitize_monthly_data(lines)
    lines = [_.split() for _ in lines]
    #take only jobs:
    data = [_ for _ in lines if not "." in _[1]]
    N = len(data)
    efficiency = [float(_[5].strip()) for _ in data]
    ncpus = [float(_[7].strip()) for _ in data]
    fig, ax = plt.subplots()
    hist = ax.hist2d(efficiency, ncpus, bins=(xbins, ybins), norm=colors.LogNorm())
    if logy:
        ax.set_yscale('log')
    plt.colorbar(hist[3], ax=ax)
    plt.ylabel('Number of cores')
    plt.xlabel('Efficiency (100*used/avail)')
    plt.title(title)
    if date_label:
        plt.text(
            hist[1][-1]*1.25, 0.05, "{}".format(time.asctime()),
            color="gray",
            ha="right", va="bottom",
            alpha=0.5,
            rotation="vertical",
        )
    plt.savefig(output_file_name, dpi=200)
    #plt.show()


def make_jobs_efficiency_used_cputime_histogram2D(
        lines, output_file_name, xbins, ybins, title=None, date_label=False, logy=False):
    lines = sanitize_monthly_data(lines)
    lines = [_.split() for _ in lines]
    #take only jobs:
    data = [_ for _ in lines if not "." in _[1]]
    N = len(data)
    efficiency = [float(_[5].strip()) for _ in data]
    used = [float(_[3].strip()) for _ in data]
    fig, ax = plt.subplots()
    hist = ax.hist2d(efficiency, used, bins=(xbins, ybins), norm=colors.LogNorm())
    if logy:
        ax.set_yscale('log')
    plt.colorbar(hist[3], ax=ax)
    plt.ylabel('Used CPU time')
    plt.xlabel('Efficiency (100*used/avail)')
    plt.title(title)
    if date_label:
        plt.text(
            hist[1][-1]*1.25, 0.05, "{}".format(time.asctime()),
            color="gray",
            ha="right", va="bottom",
            alpha=0.5,
            rotation="vertical",
        )
    plt.savefig(output_file_name, dpi=200)
    #plt.show()

def make_unused_and_cummulative_cpu_histogram(
        lines, output_file_name, xbins, title, date_label):
    lines = sanitize_monthly_data(lines)
    lines = [_.split() for _ in lines]
    #take only jobs:
    data = [_ for _ in lines if not "." in _[1]]
    N = len(data)
    hist_data = np.array([float(_[6].strip())/3600 for _ in data])
    xlimit = hist_data.mean()+3*hist_data.std()#hist_data.max()#500
    ylimit = lambda x: x.mean()*2
    plt.subplot(2, 1, 1)
    n, bins, _patches = plt.hist(
            hist_data, xbins, facecolor='xkcd:deep blue', alpha=0.75,
            range=(hist_data.min(), xlimit),
    )

    axes = plt.gca()
    axes.set_xlim([0, xlimit])
    axes.set_ylim([0, ylimit(n)])
    plt.ylabel('Number of jobs', fontsize="small")
    #plt.xlabel('CPU core hours')
    plt.title(title)
    axes.tick_params(labelsize="small")
    plt.subplot(2, 1, 2)
    hist_data.sort()
    
    #cum_hist_data = hist_data.cumsum()
    #print(hist_data)
    #print(cum_hist_data)
    #print()
    # n, bins, patches = plt.hist(
    #         cum_hist_data, xbins, facecolor='purple', alpha=0.75,
    #         range=(cum_hist_data.min(), xlimit),
    #         #cumulative=True,
    # )

    cum_hist_data_list = []
    for y in bins[1:]:
        hist_data_i = (hist_data < y)*hist_data
        cum_hist_data_list.append(hist_data_i.sum())
    cum_hist_data = np.array(cum_hist_data_list)

    left = bins[:-1]
    right = bins[1:]
    bottom = np.zeros(len(left))
    top = bottom + cum_hist_data
    XY = np.array([[left, left, right, right], [bottom, top, top, bottom]]).T

    barpath = path.Path.make_compound_path_from_polys(XY)
    patch = patches.PathPatch(barpath, color="purple")
    
    axes = plt.gca()
    axes.add_patch(patch)
    
    #axes.set_xlim([0,xlimit])
    axes.set_xlim(left[0], right[-1])
    axes.set_ylim(bottom.min(), top.max())
    plt.ylabel('Accumulated CPUh', fontsize="small")
    plt.xlabel('CPU hours', fontsize="small")
    axes.tick_params(labelsize="small")
    if date_label:
        plt.text(
            bins[-1]*1.1, 0.05, "{}".format(time.asctime()),
            color="gray",
            ha="right", va="bottom",
            alpha=0.5,
            rotation="vertical",
        )
    plt.savefig(output_file_name, dpi=200)
    #plt.show()

def make_jobs_walltime_histogram(
        lines, output_file_name, xbins, title=None, date_label=False):
    lines = sanitize_monthly_data(lines)
    lines = [_.split() for _ in lines]
    #take only jobs:
    data = [_ for _ in lines if not "." in _[1]]
    N = len(data)
    hist_data = [round(float(_[2].strip())/86400) for _ in data]
    n, bins, patches = plt.hist(hist_data, range(xbins), facecolor='#993300', alpha=0.75)
    axes = plt.gca()
    #axes.set_xlim([0, 100])
    plt.ylabel('Number of jobs')
    plt.xlabel('Wall clock time (days)')
    plt.title(title)

    if date_label:
        plt.text(
            bins[-1]*1.1, 0.05, "{}".format(time.asctime()),
            color="gray",
            ha="right", va="bottom",
            alpha=0.5,
            rotation="vertical",
        )
    plt.savefig(output_file_name, dpi=200)

