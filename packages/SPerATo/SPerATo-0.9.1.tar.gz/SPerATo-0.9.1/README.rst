SPerATo package
===============

(**S**\ lurm jobs **Per**\ formance **A**\ nalysis **To**\ ol)

A basic tool to summarize global performance of slurm jobs.


Warning!
--------

.. figure:: in-progress-icon-2.jpg
    :width: 200px
    :align: center
    :height: 200px
    :alt: work in progress
    :figclass: align-center

    This is work in progress!


Installation
------------

* With `pip`::

    $ pip install SPerATo


Usage
-----

The package provides several executables:

``sperato-list``
  can be used to obtain a summary list of users or accounts that run jobs in a
  time period ordered by different criteria

``sperato-hkhlr``
  utility to produce some data required for the HKHLR reports
  
``sperato-plots``
  produce some efficiency plots from data obtained with other ``sperato-*``
  programs

``monitoring-plots-hkhlr``
  just a script to produce all necessary data for the monthly report to HKHLR

Each program has several options available. Use the ``-h`` option to learn more about
them.


Configuration
-------------

``SPerATo`` requires no configuration, but if the file ``$HOME/.sperato.conf``
is present, it will be used. The order followed to get values for user given
parameters is:

1. Command line. If the option is given explicitly in the command line, it
   has priority.
2. Config file. If the parameter is found there, it is taken.
3. Default. If the parameter was not found before, and there is a default
   value for it, it will be taken.

   
TODO
----

* Global CPU efficiency plot (CPU load vs time)
* A LaTeX report should be produced by ``monitoring-plots-hkhlr``, given a template

  
