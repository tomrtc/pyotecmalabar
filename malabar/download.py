#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import click

import os
import requests
import math
from posixpath import basename, dirname
from urllib.parse import urlparse
from multiprocessing import Process


def do_partialGET(wrk,url,fnp,size,fullsize):
    """Do HTTP GET with range header"""
    begin_position = wrk*size
    end_position = min(fullsize,((wrk + 1) * size) - 1)
    temporary_file = open(fnp + str(wrk) , "wb")
    req = requests.get(url,headers={'Range': 'bytes=%d-%d' % (begin_position, end_position)}, stream=True)
    current_position = begin_position
    while current_position < end_position:
        actual_size = min(4098,end_position-current_position+1)
        buffer = req.raw.read(actual_size)
        temporary_file.write(buffer)
        temporary_file.flush()
        current_position = current_position + actual_size
    temporary_file.close()

def checkURL(file_type, delivery):
    """Check with HTTP reachability"""
    head_req = requests.head(delivery[file_type])
    if not (head_req.status_code == requests.codes.ok):
        click.secho( file_type + ' HTTP HEAD failure :' + str(head_req.status_code) , fg='red')
        exit()
    else:
        return head_req

def do_fullGET(file_type, delivery, destination_directory):
    """Download full file"""
    target = os.path.join(destination_directory ,basename(urlparse(delivery[file_type]).path))
    get_req = requests.get(delivery[file_type])

    if not (get_req.status_code == requests.codes.ok):
        click.secho( file_type + ' HTTP GET failure :' + str(get_req.status_code) , fg='red')
    else:
        with open(target, 'wb') as target_file:
            target_file.write(get_req.content)
            target_file.close()
        return get_req

def download_delivery(delivery, destination_directory):
    """Downloads a template delivery set of files  from CDA with concurrent threads"""
    if not os.path.exists(destination_directory):
        os.mkdir(destination_directory)
    click.secho('downloading...' + str(os.cpu_count()) , fg='blue')
    checkURL('txt', delivery)
    checkURL('ovf', delivery)
    checkURL('mf', delivery)
    ## parralel stuff
    workers = []
    workers_number = os.cpu_count()
    vmdk_file_name = os.path.join(destination_directory ,basename(urlparse(delivery['vmdk']).path))
    vmdk_head_req = checkURL('vmdk',delivery)
    if 'content-length' in vmdk_head_req.headers:
        vmdk_size=int(vmdk_head_req.headers['content-length'])
        split_size=int(math.ceil(float(vmdk_size)/float(workers_number)))
        for idx in range(workers_number):
            worker = Process(target=do_partialGET,args=(idx, delivery['vmdk'], vmdk_file_name, split_size, vmdk_size))
            workers.append(worker)
            worker.start()
    else:
        click.secho(' HTTP failure : cannot get the vmdk size' , fg='red')
        exit()
    # Wait for all worker processes to finish
    do_fullGET('txt', delivery, destination_directory)
    do_fullGET('ovf', delivery, destination_directory)
    do_fullGET('mf', delivery, destination_directory)
    for worker in workers:
        worker.join()
    vmdk_file = open(vmdk_file_name, 'wb')
    for file_part in (vmdk_file_name+'.part'+str(i) for i in range(0,workers_number)):
        shutil.copyfileobj(open(file_part, 'rb'), vmdk_file)
        os.remove(file_part)
    vmdk_file.close()
