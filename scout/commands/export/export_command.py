#!/usr/bin/env python
# encoding: utf-8
"""
export.py

Export objects from a scout database

Created by Måns Magnusson on 2016-05-11.
Copyright (c) 2016 ScoutTeam__. All rights reserved.

"""

import logging

import click


LOG = logging.getLogger(__name__)

from .variant import variants
from .hpo import hpo_genes
from .transcript import transcripts
from .gene import genes
from .panel import panel
from .case import cases
from .mitochondrial_report import mt_report


@click.group()
@click.pass_context
def export(ctx):
    """
    Export objects from the mongo database.
    """
    LOG.info("Running scout export")

export.add_command(panel)
export.add_command(genes)
export.add_command(transcripts)
export.add_command(variants)
export.add_command(hpo_genes)
export.add_command(cases)
export.add_command(mt_report)
