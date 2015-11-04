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
import pickle
import os

from .feeder import fetch_ovf_from_rss
from .download import download_delivery
from .ovf import instanciate_ovf

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.secho('Malabar {}'.format(malabar.__version__), fg='green')
    ctx.exit()
def init_delivery(name, destination_directory):
    base_dir = os.path.join(destination_directory, name)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return base_dir

def save_delivery(delivery, name, base_directory):
    pkl_file_name = os.path.join(base_directory, name + '.pkl')
    with open(pkl_file_name, 'w+b') as output:
        pickle.dump(delivery, output, pickle.HIGHEST_PROTOCOL)


def get_delivery(name, base_directory):
    """Read a delivery dictionary from disk."""
    pkl_file_name = os.path.join(base_directory, name + '.pkl')
    try:
        with open(pkl_file_name, "r+b") as input:
            delivery = pickle.load(input)
    except FileNotFoundError:
        delivery = {}
    return delivery


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
    delivery_directory = init_delivery(name, obj.getSettings('otec')['ovf-directory'])
    delivery = fetch_ovf_from_rss(name, obj.getSettings('otec')['rss-uri'], RSS_DATABASE_FILE_PATH)
    download_delivery(delivery, delivery_directory)
    save_delivery(delivery, name, delivery_directory)



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
    click.secho('fetch', fg='green')


@contextlib.contextmanager
def omi_channel(host, username,  password, port):
    omi = connect.SmartConnect(
        host=host,
        user=username,
        pwd=password,
        port=port)
    click.secho("current session id: {}".format(omi.content.sessionManager.currentSession.key), fg='yellow')
    click.secho("Connected on {}:".format(host), fg='yellow')
    yield omi
    connect.Disconnect(omi)
    click.secho("DisConnected of {}:".format(host), fg='yellow')

def dump(obj):
   for attr in dir(obj):
       if hasattr(obj, attr):
           print("obj.%s = %s" % (attr, getattr(obj, attr)))

def view(ccc):
    '''view container'''
    container = ccc.viewManager.CreateContainerView(ccc.rootFolder, [vim.VirtualMachine], True)
    for c in container.view:
        yield c.config.name, c.config.uuid

def listhosts(ccc):
    '''view container'''
    pp = pprint.PrettyPrinter(indent=4)
    container = ccc.viewManager.CreateContainerView(ccc.rootFolder, [vim.HostSystem], True)
    for c in container.view:
        return c

def listnetwork(ccc):
    '''view container'''
    pp = pprint.PrettyPrinter(indent=4)
    container = ccc.viewManager.CreateContainerView(ccc.rootFolder, [vim.Network], True)
    for c in container.view:
        return c


@cli.command('listvm')
@click.pass_obj
def listvm(obj):
    '''List VMs'''
    with omi_channel(obj.getSettings('otec')['host'], obj.getSettings('otec')['user'], obj.getSettings('otec')['password'], 443) as channel:
        content = channel.RetrieveContent()
        click.secho("list the availlable VM on {}/{}:".format(obj.getSettings('otec')['host'], content.about.fullName), fg='magenta')
        for vm_name, vm_uuid in view(content):
            click.secho(" {} : {}".format(vm_name, vm_uuid), fg='magenta')


@cli.command('deployovf')
@click.argument('name')
@click.pass_obj
def deployovf(obj, name):
    '''Deploy VMs'''
    click.secho('deploy ...', fg='blue')
    delivery_directory = init_delivery(name, obj.getSettings('otec')['ovf-directory'])
    delivery = get_delivery(name, delivery_directory)
    if not delivery:
        click.secho('fetch before : malabar fetch ' + name, fg='red')
        exit(3)
    ##
    with omi_channel(obj.getSettings('otec')['host'], obj.getSettings('otec')['user'], obj.getSettings('otec')['password'], 443) as channel:
        content = channel.RetrieveContent()
        datacenter = content.rootFolder.childEntity[0]
        datastore = datacenter.datastoreFolder.childEntity[0]
        vmfolder = datacenter.vmFolder
        otec_network = listnetwork(content)
        host = listhosts(content)
        resource_pools = datacenter.hostFolder.childEntity
        resource_pool = resource_pools[0].resourcePool
        #    click.secho(" {}".format(nh), fg='magenta')
        try:
            instanciate_ovf(delivery, channel, host, vmfolder,
            resource_pool, datastore, otec_network)

        except vmodl.MethodFault as vmomi_fault:
            click.secho("WMvare error: {}".format(vmomi_fault.msg), fg='red')
        except Exception as std_exception:
            click.secho("standard error: {}".format(str(std_exception)), fg='red')


@cli.command('note')
@click.argument('uuid')
@click.argument('note')
@click.pass_obj
def notevm(obj, uuid, note):
    '''ovf extract '''
    with omi_channel(obj.getSettings('otec')['host'], obj.getSettings('otec')['user'], obj.getSettings('otec')['password'], 443) as channel:
        vm = channel.content.searchIndex.FindByUuid(None, uuid, True)
        if vm:
            click.secho("⇒❯ {}".format(vm.name), fg='magenta')
            try:
                spec = vim.vm.ConfigSpec()
                spec.annotation = note
                vm.ReconfigVM_Task(spec)
            except vmodl.MethodFault as vmomi_fault:
                click.secho("WMvare error: {}".format(vmomi_fault.msg), fg='red')
            except Exception as std_exception:
                click.secho("standard error: {}".format(str(std_exception)), fg='red')
        else:
            click.secho("No matching VM for {}".format(uuid), fg='red')

@cli.command('vmmac')
@click.argument('uuid')
@click.pass_obj
def vmmac(obj, uuid):
    '''ovf extract '''
    pp = pprint.PrettyPrinter(indent=4)
    with omi_channel(obj.getSettings('otec')['host'], obj.getSettings('otec')['user'], obj.getSettings('otec')['password'], 443) as channel:
        vm = channel.content.searchIndex.FindByUuid(None, uuid, True)
        if vm:
            try:
                nics = [dev for dev in vm.config.hardware.device
                        if isinstance(dev, vim.vm.device.VirtualEthernetCard)]
                for nic in nics:
                     click.secho("{} ⇒❯ Nic {} on {} ".format(vm.name, nic.macAddress, nic.backing.network.name), fg='magenta')
                disks = [d for d in vm.config.hardware.device
                         if isinstance(d, vim.vm.device.VirtualDisk) and
                         isinstance(d.backing, vim.vm.device.VirtualDisk.FlatVer2BackingInfo)]
                #pp.pprint(disks)
                for disk in disks:
                    click.secho("{} ⇒❯ Disk {} on {} ".format(vm.name, disk.deviceInfo.label, disk.backing.fileName), fg='magenta')
            except vmodl.MethodFault as vmomi_fault:
                click.secho("WMvare error: {}".format(vmomi_fault.msg), fg='red')
            except Exception as std_exception:
                click.secho("standard error: {}".format(str(std_exception)), fg='red')
        else:
            click.secho("No matching VM for {}".format(uuid), fg='red')
