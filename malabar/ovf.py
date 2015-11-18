#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import click
import os
import math
import pprint
import time
from .download import HTTP_CHUNKED_SIZE
import pyVmomi
import requests
from requests_toolbelt.streaming_iterator import StreamingIterator

def readVMDK(vmdkfile, filesize, lease):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: HTTP_CHUNKED_SIZE.
    lease is the current http conection that must be refreshed in oprder to avoid timout condition from ESX."""
    current = 0
    step_size = int(math.ceil(float(filesize)/float(HTTP_CHUNKED_SIZE * 100)))
    step = 0
    last_refresh = HTTP_CHUNKED_SIZE * 100
    with click.progressbar(length=step_size,
                           label='Upload template') as bar:
        while True:
            blk_size = min(HTTP_CHUNKED_SIZE,  filesize - current + 1)
            data = vmdkfile.read(blk_size)
            if not data:
                break
            current = current + blk_size
            last_refresh = last_refresh - blk_size
            if last_refresh < 0:
                last_refresh = HTTP_CHUNKED_SIZE * 100
                step = step + 1
                progress = int(math.ceil(float(step - 1)/float(step_size) * 100.0))
                bar.update(1)
                lease.Progress(progress)
            #lease.Progress(11)
            yield data

def instanciate_ovf(delivery, vmname, omi, host, folder, resource_pool, datastore, otec_network):
    """instanciate a template delivery set of files  from CDA to ESXi"""
    pp = pprint.PrettyPrinter(indent=4)

    try:
        with  open(delivery["ovf-cache"]) as ovf_file:
            ovf_descriptor = ovf_file.read()
    except:
        click.secho('Local file error :' + delivery["ovf-cache"] + ' ', fg='red')
        exit(2)

    vmdk_file = open(delivery["vmdk-cache"], 'rb')
    vmdk_size = os.path.getsize(delivery["vmdk-cache"])
    ovf_manager = omi.content.ovfManager
    pdp = pyVmomi.vim.OvfManager.ParseDescriptorParams()
    pdr = ovf_manager.ParseDescriptor(ovf_descriptor, pdp)
    vhr = ovf_manager.ValidateHost(ovf_descriptor, host, pyVmomi.vim.OvfManager.ValidateHostParams())
    click.secho("Deploy {} with {} on {}:".format(delivery["ovf-cache"], delivery["vmdk-cache"], host), fg='green')
    click.secho("Ovf parsing {} errors {} warnings.".format(len(pdr.error), len(pdr.warning)), fg='green')
    for error in pdr.error:
        click.secho("Ovf parsing error: {}".format(error.msg), fg='red')
    click.secho("Validate host  {} errors {} warnings.".format(len(vhr.error), len(vhr.warning)), fg='green')
    for error in vhr.error:
        click.secho("Validate host error: {}".format(error.msg), fg='red')
    parameters = pyVmomi.vim.OvfManager.CreateImportSpecParams()
    parameters.entityName = vmname
    parameters.locale = "US"
    parameters.diskProvisioning = "thin"
    parameters.networkMapping.append(pyVmomi.vim.OvfManager.NetworkMapping(name='otec-net', network=otec_network))
    isr = ovf_manager.CreateImportSpec(ovf_descriptor,
                                       resource_pool,
                                       datastore,
                                       parameters)
    click.secho("Ovf Import Specification  {} errors {} warnings.".format(len(isr.error), len(isr.warning)), fg='green')
    for error in isr.error:
        click.secho("Ovf Import Specification error: {}".format(error.msg), fg='red')
    for warning in isr.warning:
        click.secho("Ovf Import Specification warning: {}".format(warning.msg), fg='red')

    nfc_lease = resource_pool.ImportVApp(isr.importSpec, folder, host)
    with click.progressbar(length=100,
                           label='Initializing ') as bar:
        nv=0
        while nfc_lease.state == 'initializing':
            time.sleep(0.1)
            v = nv
            nv = nfc_lease.initializeProgress
            bar.update(nv - v)
    if  nfc_lease.state == 'error':
         click.secho("ImportVM error: {}".format(nfc_lease.error.msg), fg='red')
         return

    for dev_url in nfc_lease.info.deviceUrl:
        #click.secho("NFC target URL  {}".format(dev_url), fg='green')
        if dev_url.disk:
                diskurl = dev_url.url

    if not diskurl:
         click.secho("ImportVM error no disk url found ???", fg='red')
         return

    headers = {'user-agent': 'malabar/1.0',
               'Content-Type': 'application/x-vnd.vmware-streamVmdk',
               'Connection': 'Keep-Alive', 'Content-Length': str(vmdk_size)}

    stream = StreamingIterator(vmdk_size, readVMDK(vmdk_file, vmdk_size, nfc_lease))
    post_req = requests.post(diskurl, headers=headers, verify=False, data=stream)

    nfc_lease.Complete()
    #nfc_lease.Abort()
    vmdk_file.close()
    return nfc_lease.info.entity
