#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import click

import os
import requests
import math
from shutil import copyfileobj
from posixpath import basename, dirname
from urllib.parse import urlparse
import pprint

from .download import checkURL
from .download import HTTP_CHUNKED_SIZE


def instanciate_ovf(delivery, omi, host):
    """instanciate a template delivery set of files  from CDA to ESXi"""

    try:
        with  open(delivery["ovf-cache"]) as ovf_file:
            ovf_descriptor = ovf_file.read()
    except:
        click.secho('Local file errot :' + delivery["ovf-cache"] + ' ' + str(head_req.status_code) , fg='red')
        exit(2)

    vmdk_file = open(delivery["vmdk-cache"], 'rb')
    vmdk_size = os.path.getzize(delivery["vmdk-cache"])
    step_size = int(math.ceil(float(vmdk_size)/float(1000)))
    click.secho("Deploy {} with {} on {}:".format(host,delivery["ovf-cache"], delivery["vmdk-cache"]), fg='green')
    click.secho("Size {} with {} steps.".format(vmdk_size, step_size), fg='green')
    ovf_manager = omi.content.ovfManager
    pdr = ovf_manager.ParseDescriptor(ovf_descriptor, ovf_manager.ParseDescriptorParams())
    vhr = ovf_manager.ValidateHostovf_descriptor, host, ovf_manager.ValidateHostParams()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(delivery)
    pp.pprint(pdr)
    pp.pprint(vhr)
    vmdk_file.close()





#     spec_params = ovf_manager.CreateImportSpecParams()
#     import_spec = ovf_manager.CreateImportSpec(ovf_descriptor,
#                                            objs["resource pool"],
#                                            objs["datastore"],
#                                            spec_params)
# parse_descriptor_result = content.
#         validate_host_result = content.ovfManager.
#                 ovf_descriptor,
#                 host,
#                 pyVmomi.vim.OvfManager.)
#         create_import_spec_result = content.ovfManager.CreateImportSpec(
#                 ovf_descriptor,
#                 resource_pool,
#                 datastore,
#                 pyVmomi.vim.OvfManager.CreateImportSpecParams())
#         import_spec = create_import_spec_result.importSpec
#         http_nfc_lease = resource_pool.ImportVApp(
#                 import_spec,
#                 folder,
#                 host)
# # TODO: Make http requests as specified by the http_nfc_lease:

#         # * Wait until http_nfc_lease.state changes to ready.
#         while http_nfc_lease.state != 'ready':
#             time.sleep(0.5)

#         # * Make HTTP Post requests to the URLS provided in the http_nfc_lease
#         #   with the disk contents, etc. as data.
#         upload_count = len(http_nfc_lease.info.deviceUrl)
#         progress = (100 * n // upload_count for n in range(upload_count))
#         for device_url in http_nfc_lease.info.deviceUrl:
#             http_nfc_lease.Progress(next(progress))
#             url = device_url.url
#             code.interact(local=locals())
#             # TODO: Figure out which file should be uploaded
#             data = None
#             # TODO: Figure out how to keep the http_nfc_lease from timing out
#             # during this request
#             requests.post(url, data)

#         #TODO: replace the following with http_nfc_lease.Complete()
#         http_nfc_lease.Abort()
#     vmdk_file.close()
#  objs = get_objects(si, args)

#     lease = objs["resource pool"].ImportVApp(import_spec.importSpec)
#     while(True):
#         if (lease.state == vim.HttpNfcLease.State.ready):
#             # Assuming single VMDK.
#             url = lease.info.deviceUrl[0].url.replace('*', args.host)
#             # Spawn a dawmon thread to keep the lease active while POSTing
#             # VMDK.
#             keepalive_thread = Thread(target=keep_lease_alive, args=(lease,))
#             keepalive_thread.start()
#             # POST the VMDK to the host via curl. Requests library would work
#             # too.
#             curl_cmd = (
#                 "curl -Ss -X POST --insecure -T %s -H 'Content-Type: \
#                 application/x-vnd.vmware-streamVmdk' %s" %
#                 (args.vmdk_path, url))
#             system(curl_cmd)
#             lease.HttpNfcLeaseComplete()
#             keepalive_thread.join()
#             return 0
#         elif (lease.state == vim.HttpNfcLease.State.error):
#             print "Lease error: " + lease.state.error
#             exit(1)
