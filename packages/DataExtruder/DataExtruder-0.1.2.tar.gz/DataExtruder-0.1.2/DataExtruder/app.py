#!/usr/bin/env python

import logging
import click
from datasource import load_data
from render_data import compile_data
from helper import get_config,set_var_by_env

logger = logging.getLogger()

@click.command()
@click.option('--log-level', default="INFO", help='Log-Level')
@click.option('--config', default="config.json", help='Config file to use')
@click.option('--target', default="target", help='Where to store the files created')
@click.option('--template', prompt='Which template to use')
def main(log_level, config, target, template):
    """Render the data."""
    logging.basicConfig(level=log_level)

    config = get_config(config)
    config = set_var_by_env(config,"DATAEXTRUDER_DIRECTUS_PASSWORD","password")
    config = set_var_by_env(config,"DATAEXTRUDER_DIRECTUS_username","username")

    data = load_data(config)
    compile_data(template,target, data)

if __name__ == '__main__':
    main()