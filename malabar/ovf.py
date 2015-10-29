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
import pyVmomi


def instanciate_ovf(delivery, omi, host):
    """instanciate a template delivery set of files  from CDA to ESXi"""

    try:
        with  open(delivery["ovf-cache"]) as ovf_file:
            ovf_descriptor = ovf_file.read()
    except:
        click.secho('Local file error :' + delivery["ovf-cache"] + ' ', fg='red')
        exit(2)

    vmdk_file = open(delivery["vmdk-cache"], 'rb')
    vmdk_size = os.path.getsize(delivery["vmdk-cache"])
    step_size = int(math.ceil(float(vmdk_size)/float(HTTP_CHUNKED_SIZE * 100)))

    ovf_manager = omi.content.ovfManager
    pdr = ovf_manager.ParseDescriptor(ovf_descriptor, pyVmomi.vim.OvfManager.ParseDescriptorParams())
    vhr = ovf_manager.ValidateHost(ovf_descriptor, host, pyVmomi.vim.OvfManager.ValidateHostParams())
    click.secho("Deploy {} with {} on {}:".format(delivery["ovf-cache"], delivery["vmdk-cache"], host), fg='green')

    click.secho("VMDK Size {} with {} steps.".format(vmdk_size, step_size), fg='green')
    pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(delivery)
    #pp.pprint(pdr)
    #pp.pprint(vhr)
    click.secho("Ovf parsing {} errors {} warnings.".format(len(pdr.error), len(pdr.warning)), fg='green')
    for error in pdr.error:
        click.secho("Ovf parsing error: {}".format(error.msg), fg='red')
    click.secho("Validate host  {} errors {} warnings.".format(len(vhr.error), len(vhr.warning)), fg='green')
    for error in vhr.error:
        click.secho("Validate host error: {}".format(error.msg), fg='red')
    vmdk_file.close()


   # for dev_url in lease.info.deviceUrl:
   #          filename = dev_url.targetId
   #          hostname = urlparse(s._proxy.binding.url).hostname
   #          upload_url = dev_url.ulr.replace("*", hostname)
   #          filename = os.path.join(os.path.dirname(OVF_FILE), filename)
   #          fsize = os.stat(filename).st_size
   #          f = open(filename,'rb')
   #          mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
   #          request = urllib2.Request(upload_url, upload_url=mmapped_file)

   #          request.add_header("Content-Type", "application/x-vnd.vmware-streamVmdk")
   #          request.add_header("Connection", "Keep-Alive")
   #          request.add_header("Content-Length", str(fsize))
   #          opener = urllib2.build_opener(urllib2.HTTPHandler)
   #          resp = opener.open(request)
   #          mmapped_file.close()
   #          f.close()

   #      go_on = False
   #      t.join()
   #      request = VI.HttpNfcLeaseCompleteRequestMsg()
   #      _this =request.new__this(http_nfc_lease)
   #      _this.set_attribute_type(http_nfc_lease.get_attribute_type())
   #      request.set_element__this(_this)
   #      s._proxy.HttpNfcLeaseComplete(request)

   #  finally:
   #      s.disconnect()


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
