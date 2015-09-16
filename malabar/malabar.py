#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import time

import click
from clickclick import AliasedGroup, Action

from configparser import ConfigParser

import malabar
from .config import CONFIGURATION_FILE_NAME, get_configuration


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Malabar {}'.format(malabar.__version__))
    ctx.exit()


# CLI handling

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.option('--config-file', '-c', help='Use alternative configuration file',
              default=CONFIGURATION_FILE_NAME, metavar='PATH')
@click.option('-V', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True,
              help='Print the current version number and exit.')

@click.pass_context
def cli(ctx,   config_file):
    ctx.obj = get_configuration(config_file)


@cli.command('list')
@click.pass_obj
def list_tokens(obj):
    '''List tokens'''
    print(obj)


@cli.command('fetch')
@click.argument('name')
@click.pass_obj
def fetch_template(obj, name):
    '''fetch a named template'''
    print("fetch")


@cli.command('esxi')
@click.option('--host', help='hostname', metavar='HOST')
@click.option('-U', '--user', help='Username to use for authentication', envvar='USER', metavar='NAME')
@click.option('-p', '--password', help='Password to use for authentication', envvar='MALABAR_PASSWORD', metavar='PWD')
@click.option('--insecure', help='Do not verify SSL certificate', is_flag=True, default=False)
@click.pass_obj
def esxi(obj, host, name, user, password, insecure):
    '''Connect to host with API.'''
    print(host)
    # Build a view and get basic properties for all Virtual Machines
    objView = content.viewManager.CreateContainerView(content.rootFolder, viewType, True)
    tSpec = vim.PropertyCollector.TraversalSpec(name='tSpecName', path='view', skip=False, type=vim.view.ContainerView)
    pSpec = vim.PropertyCollector.PropertySpec(all=False, pathSet=props, type=specType)
    oSpec = vim.PropertyCollector.ObjectSpec(obj=objView, selectSet=[tSpec], skip=False)
    pfSpec = vim.PropertyCollector.FilterSpec(objectSet=[oSpec], propSet=[pSpec], reportMissingObjectsInResults=False)
    retOptions = vim.PropertyCollector.RetrieveOptions()
    totalProps = []
    retProps = content.propertyCollector.RetrievePropertiesEx(specSet=[pfSpec], options=retOptions)
    totalProps += retProps.objects
    while retProps.token:
        retProps = content.propertyCollector.ContinueRetrievePropertiesEx(token=retProps.token)
        totalProps += retProps.objects




def main():
    cli()
