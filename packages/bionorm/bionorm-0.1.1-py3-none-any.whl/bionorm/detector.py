#!/usr/bin/env python

import os
import sys
import gzip
import click
import logging
from . import Detector


@click.command()
@click.option('--target', multiple=True,
              help='''TARGETS can be files or directories or both''')
@click.option('--no_busco', is_flag=True,
              help='''Disable BUSCO''')
@click.option('--no_nodes', is_flag=True,
              help='''Disable DSCensor Stats and Node Generation''')
@click.option('--log_file', metavar='<FILE>',
              default='./bionorm.log',
              help='''File to write log to. (default:./bionorm.log)''')
@click.option(
    '--log_level',
    metavar='<LOGLEVEL>',
    default='INFO',
    help='''Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default:INFO)''')
# @click.option('--normalize', is_flag=True,
#             help='''Normalizes provided files.
# Incongruencies in FASTA will be corrected if the provided genome name
# passes checks.
# The gff file will be tidied if it fails gff3 validation in gt:
#    gt gff3 -sort -tidy -retainids input.gff3 > out.gff3
# ''')
def cli(target, no_busco, no_nodes, log_file, log_level):
    '''incongruency_detector:

        Detect Incongruencies with LIS Data Store Standard
    '''
    if not target:
        print('Must specify at least one --target.  Run with --help for usage')
        sys.exit(1)
    data_store_home = os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))
    templates_dir = '{}/templates'.format(data_store_home)
    readme_template = '{}/template__README.KEY.yml'.format(templates_dir)
    options = {'log_level': log_level, 'log_file': log_file,
               'no_busco': no_busco, 'no_nodes': no_nodes,
               'readme_template': readme_template}
    for t in target:
        detector = Detector(t, **options)  # initializers
        detector.detect_incongruencies()  # class method runs all detection methods


if __name__ == '__main__':
    cli()
