#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import click
from clickclick import AliasedGroup


import malabar
from .config import CONFIGURATION_FILE_NAME
from .config import RSS_DATABASE_FILE_PATH
from .config import get_configuration
from .config import create_default_config_file
import pprint

from .feeder import fetch_ovf_from_rss
from .download import download_delivery


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.secho('Malabar {}'.format(malabar.__version__), fg='green')
    ctx.exit()


# CLI handling

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.option('--config-file', '-c', help='Use alternative configuration file',
              default=CONFIGURATION_FILE_NAME, metavar='PATH')
@click.option('-V', '--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help='Print the current version number and exit.')
@click.pass_context
def cli(ctx,   config_file):
    ctx.obj = get_configuration(config_file)


@cli.command('list')
@click.pass_obj
def list(obj):
    '''List'''
    click.secho(obj.getDefaultSettings(), fg='blue')


@cli.command('init')
@click.pass_obj
def init(obj):
    '''init'''
    create_default_config_file()
    click.secho('Init Path: %s' % click.format_filename(CONFIGURATION_FILE_NAME), bold=True, fg='green')



@cli.command('fetch')
@click.argument('name')
@click.pass_obj
def fetch_template(obj, name):
    '''fetch a named template'''
    click.secho('fetching ...', fg='blue')
    delivery = fetch_ovf_from_rss(name, obj.getSettings('otec')['rss-uri'], RSS_DATABASE_FILE_PATH)
    pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(delivery)
    download_delivery(delivery, "/tmp")


@cli.command('esxi')
@click.option('--host', help='hostname', metavar='HOST')
@click.option('-U', '--user', help='Username to use for authentication',
              envvar='USER', metavar='NAME')
@click.option('-p', '--password', help='Password to use for authentication',
              envvar='MALABAR_PASSWORD', metavar='PWD')
@click.option('--insecure', help='Do not verify SSL certificate',
              is_flag=True, default=False)
@click.pass_obj
def esxi(obj, hostname, user, password, insecure):
    '''Connect to host with API.'''
    print(hostname)
    click.secho('fetch', fg='green')

    # Build a view and get basic properties for all Virtual Machines
    #objView = content.viewManager.CreateContainerView(content.rootFolder, viewType, True)
    #tSpec = vim.PropertyCollector.TraversalSpec(name='tSpecName', path='view', skip=False, type=vim.view.ContainerView)
    # pSpec = vim.PropertyCollector.PropertySpec(all=False, pathSet=props, type=specType)
    # oSpec = vim.PropertyCollector.ObjectSpec(obj=objView, selectSet=[tSpec], skip=False)
    # pfSpec = vim.PropertyCollector.FilterSpec(objectSet=[oSpec], propSet=[pSpec], reportMissingObjectsInResults=False)
    # retOptions = vim.PropertyCollector.RetrieveOptions()
    # totalProps = []
    # retProps = content.propertyCollector.RetrievePropertiesEx(specSet=[pfSpec], options=retOptions)
    # totalProps += retProps.objects
    # while retProps.token:
    #     retProps = content.propertyCollector.ContinueRetrievePropertiesEx(token=retProps.token)
    #     totalProps += retProps.objects
