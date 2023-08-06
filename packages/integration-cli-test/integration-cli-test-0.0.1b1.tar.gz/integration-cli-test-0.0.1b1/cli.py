import os
import click
from smart_cli.generators.structure import Structure


@click.group()
def cli():
    pass


@cli.command()
@click.option('--name', default='project',
              help='This name of your project')
@click.argument('name', type=click.STRING, default='project', required=True)
@click.option('--type', default='basic',
              help='Choose type of your project(oauth, basic)')
@click.argument('type', type=click.STRING, default='basic', required=True)
def init(name, type):
    if type.lower() not in ['basic', 'oauth']:
        print(f"{type} invalid integration type, must be on of {['basic', 'oauth']}")
        return None
    struct = Structure(name, type)
    struct.install_dependencies()
    struct.init_django_app()
    struct.rewrite_basic_files()
    struct.generate_api_apps_files()
