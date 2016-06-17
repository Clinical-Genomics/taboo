# -*- coding: utf-8 -*-
import logging

import click

from taboo.constants import TYPES
from taboo.store.models import Sample
from .bcf import load_bcf
from .excel import load_excel

log = logging.getLogger(__name__)


@click.command()
@click.option('-k', '--include-key', help='prefix for relevant samples')
@click.option('-f', '--force', is_flag=True)
@click.argument('input_file', type=click.Path(exists=True))
@click.pass_context
def load(context, include_key, force, input_file):
    """Load data from genotype resources."""
    if input_file.endswith('.xlsx'):
        log.info('loading analyses from Excel book: %s', input_file)
        analyses = load_excel(input_file, include_key=include_key)
    elif input_file.endswith('.bcf'):
        log.info('loading analyses from BCF file: %s', input_file)
        snps = context.obj['db'].snps()
        analyses = load_bcf(input_file, snps)

    for analysis in analyses:
        log.debug('loading analysis for sample: %s', analysis.sample_id)
        is_saved = context.obj['db'].add_analysis(analysis, replace=force)
        if is_saved:
            log.info('loaded analysis for sample: %s', analysis.sample_id)
        else:
            log.warn('found previous analysis, skip: %s', analysis.sample_id)


@click.command()
@click.option('-a', '--analysis', type=click.Choice(TYPES))
@click.argument('sample_id')
@click.pass_context
def delete(context, analysis, sample_id):
    """Delete analyses and samples from the database."""
    taboo_db = context.obj['db']
    if analysis:
        log.info("deleting analysis: %s, %s", sample_id, analysis)
        old_analysis = taboo_db.analysis(sample_id, analysis).first()
        if old_analysis is None:
            log.error("analysis not loaded in database")
            context.abort()
        taboo_db.delete_analysis(old_analysis)
    else:
        log.info("deleting sample: %s", sample_id)
        old_sample = Sample.query.get(sample_id)
        if old_sample is None:
            log.error("sample not loaded in database")
            context.abort()
        old_sample.delete()
        taboo_db.save()