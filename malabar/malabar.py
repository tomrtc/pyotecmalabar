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
import contextlib

from .feeder import fetch_ovf_from_rss
from .download import download_delivery

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

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


@contextlib.contextmanager
def omi_channel(host, username,  password, port):
    omi = connect.SmartConnect(
            host=host,
            user=username,
            pwd=password,
            port=port)
    click.secho("current session id: {}".format(omi.content.sessionManager.currentSession.key), fg='red')
    click.secho("Connected on {}:".format(host), fg='yellow')
    yield omi
    connect.Disconnect(omi)
    click.secho("DisConnected of {}:".format(host), fg='red')


def dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))




def view(ccc):
    '''view container'''
    container = ccc.viewManager.CreateContainerView(ccc.rootFolder, [vim.VirtualMachine], True)
    for c in container.view:
        yield c.config.name, c.config.uuid


@cli.command('listvm')
@click.pass_obj
def listvm(obj):
    '''List VMs'''
    with omi_channel(obj.getSettings('otec')['host'], obj.getSettings('otec')['user'], obj.getSettings('otec')['password'], 443) as channel:
        content = channel.RetrieveContent()
        click.secho("list the availlable VM on {}/{}:".format(obj.getSettings('otec')['host'], content.about.fullName), fg='magenta')
        for vm_name, vm_uuid in view(content):
              click.secho(" {} : {}".format(vm_name,vm_uuid), fg='magenta')
