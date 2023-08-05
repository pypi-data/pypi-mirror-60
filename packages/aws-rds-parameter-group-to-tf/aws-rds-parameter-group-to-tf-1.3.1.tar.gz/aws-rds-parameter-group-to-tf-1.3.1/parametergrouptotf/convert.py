#!/usr/bin/env python3
#
# Convert RDS parameter group intom a TF parameter group.
#
# Usage:
#   aws rds describe-db-parameters --db-parameter-group-name your-parameter-group-name | python3 convert.py
#

import json
import sys
import subprocess
import click

VERSION = '1.3.1'

__version__ = VERSION
__author__ = 'Lev Kokotov <lev.kokotov@instacart.com>'

# Update this list if RDS decides to add more sources or you want to change
# the order in which the parameters get printed.
PARAMETERS_SOURCES_ORDER = ['system', 'user', 'engine-default']

def main(body, name='parameter_group_name'):
    if 'Parameters' not in body:
        print('Input is not valid AWS CLI response JSON object with "Parameters" key required.')
        exit(1)

    parameters = body['Parameters']

    print('resource "aws_db_parameter_group" "{name}" {{'.format(name=name)) # {{ escapes { in a format string.

    for source in PARAMETERS_SOURCES_ORDER:
        for parameter in filter_parameters(parameters, source):
            write_parameter(parameter)

    print('}')


def filter_parameters(parameters, source):
    return filter(lambda p: p['Source'] == source, parameters)


def write_parameter(parameter):
    if not parameter['IsModifiable']:
        return
    if 'ParameterValue' not in parameter:
        return
    apply_method = 'immediate' if parameter['ApplyType'] == 'dynamic' else 'pending-reboot'
    print('  # source: {}'.format(parameter['Source']))
    print('  parameter {')
    print('    apply_method = "{}"'.format(apply_method))
    print('    name         = "{}"'.format(parameter['ParameterName']))
    print('    value        = "{}" # {}'.format(parameter['ParameterValue'], parameter['Description'].replace('\n', ' ').strip()))
    print('  }\n')


@click.command()
@click.option('--name', required=False, help='The name of the parameter group in RDS.')
@click.option('--stdin/--internal', required=False, help='Get the JSON payload from stdin instead.')
def cli(name, stdin):
    if name:
        result = subprocess.check_output(['aws', 'rds', 'describe-db-parameters', ' ', name])
        body = json.loads(result)
        main(body, name)
    elif stdin:
        body = json.loads(sys.stdin.read())
        main(body)
    else:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()
