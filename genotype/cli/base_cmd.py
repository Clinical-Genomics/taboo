"""Code for the base of the CLI"""

import codecs
import logging
import os

import click
import coloredlogs
import yaml

from genotype import __title__, __version__
from genotype.store import api

from .serve import serve_cmd

LOG = logging.getLogger(__name__)


@click.group()
@click.option('-c', '--config', default='~/.genotype.yaml',
              type=click.Path(), help='path to config file')
@click.option('-d', '--database', help='path/URI of the SQL database')
@click.option('-l', '--log-level', default='INFO')
@click.option('--log-file', type=click.Path())
@click.version_option(__version__, prog_name=__title__)
@click.pass_context
def root(context, config, database, log_level, log_file):
    """Interact with Taboo genotype comparison tool."""
    coloredlogs.install(level=log_level)

    LOG.debug("%s: version %s", __title__, __version__)

    # read in config file if it exists
    if os.path.exists(config):
        with codecs.open(config) as conf_handle:
            context.obj = yaml.load(conf_handle)
    else:
        context.obj = {}

    context.default_map = context.obj
    if context.obj.get('database') is None:
        context.obj['database'] = database

    if context.invoked_subcommand != 'serve':
        # setup database
        uri = context.obj['database'] or 'sqlite://'
        context.obj['db'] = api.connect(uri)