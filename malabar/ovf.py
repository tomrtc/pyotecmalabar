#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import click
import os
import math
import pprint
import time
from .download import HTTP_CHUNKED_SIZE
import pyVmomi


def instanciate_ovf(delivery, omi, host, folder, resource_pool, datastore, otec_network):
    """instanciate a template delivery set of files  from CDA to ESXi"""
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(delivery)
    pp.pprint(host)
    pp.pprint(folder)
    pp.pprint(resource_pool)
    pp.pprint(datastore)
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

    click.secho("Ovf parsing {} errors {} warnings.".format(len(pdr.error), len(pdr.warning)), fg='green')
    for error in pdr.error:
        click.secho("Ovf parsing error: {}".format(error.msg), fg='red')
    click.secho("Validate host  {} errors {} warnings.".format(len(vhr.error), len(vhr.warning)), fg='green')
    for error in vhr.error:
        click.secho("Validate host error: {}".format(error.msg), fg='red')
    parameters = pyVmomi.vim.OvfManager.CreateImportSpecParams()
    parameters.entityName = "rto"
    #pp.pprint(parameters)
    #parameters.networkMapping = {name:"otec-net", network: host }
    parameters.networkMapping.append(pyVmomi.vim.OvfManager.NetworkMapping(name='otec-net', network=otec_network))
    #pp.pprint(parameters.networkMapping)
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


    while nfc_lease.state != 'ready':
        time.sleep(0.1)
    for dev_url in nfc_lease.info.deviceUrl:
        click.secho("NFC target URL  {}".format(dev_url), fg='green')
    nfc_lease.Abort()
    vmdk_file.close()


   #
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


#
# parse_descriptor_result = content.
#         validate_host_result = content.ovfManager.
#                 ovf_descriptor,
#                 host,
#                 pyVmomi.vim.OvfManager.)
#         create_import_spec_result = content.ovfManager.CreateImportSpec(
#                 ovf_descriptor,
#                 resource_pool,
#                 datastore,
#                 ))
#
# # TODO: Make http requests as specified by the http_nfc_lease:

#         # * Wait until http_nfc_lease.state changes to ready.
#

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
#
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
  # Create the objects needed for the import spec
  # datacenter_list = si.content.rootFolder.childEntity
  # dc_obj = datacenter_list[0]

  # datastore_list = dc_obj.datastoreFolder.childEntity
  # ds_obj = datastore_list[0]

  # network_list = dc_obj.networkFolder.childEntity
  # net_obj = network_list[0]

  # resource_pool = dc_obj.hostFolder.childEntity[0].resourcePool



  # # Now we create the import spec
  # manager = si.content.ovfManager
  # isparams = vim.OvfManager.CreateImportSpecParams()

  # import_spec = manager.CreateImportSpec(ovfd,
  #                                        resource_pool,
  #                                        ds_obj,
  #                                        isparams)

  # print import_spec.importSpec

  # lease = resource_pool.ImportVApp(import_spec.importSpec)

  # print lease.state

  # while (True):
  #   if (lease.state == vim.HttpNfcLease.State.ready):
  #     print "Ready to rock and roll"
  #     return 0
  #   elif (lease.state == vim.HttpNfcLease.State.error):
  #     # Print some error message out if you feel so inclined.
  #     print "Failed"
  #     print lease.error
  #     sys.exit(1)
