#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import click

import os
import requests
import math
import hashlib
import configparser
import itertools
import re
import pprint
import yaml

from shutil import copyfileobj
from posixpath import basename
from urllib.parse import urlparse
from multiprocessing import Process

HTTP_CHUNKED_SIZE = 8192


# def do_partialGET(wrk, url, fnp, size, fullsize):
#     """Do HTTP GET with range header"""
#     begin_position = wrk*size
#     end_position = min(fullsize, ((wrk + 1) * size) - 1)
#     temporary_file = open(fnp + '-' + str(wrk), "wb")
#     req = requests.get(url,
#      headers={'Range': 'bytes=%d-%d' % (begin_position, end_position)},
#      stream=True)
#     current_position = begin_position
#     while current_position < end_position:
#         actual_size = min(HTTP_CHUNKED_SIZE, end_position-current_position+1)
#         buffer = req.raw.read(actual_size)
#         temporary_file.write(buffer)
#         temporary_file.flush()
#         current_position = current_position + actual_size
#     temporary_file.close()


def do_GET(url, target, fullsize):
    """Do HTTP GET"""
    begin_position = 0
    end_position = fullsize
    temporary_file = open(target, "wb")
    req = requests.get(url, stream=True)
    current_position = begin_position
    while current_position < end_position:
        actual_size = min(HTTP_CHUNKED_SIZE, end_position-current_position+1)
        buffer = req.raw.read(actual_size)
        temporary_file.write(buffer)
        temporary_file.flush()
        current_position = current_position + actual_size
    temporary_file.close()


def checkURL(fileurl):
    """Check with HTTP reachability"""
    head_req = requests.head(fileurl)
    if not (head_req.status_code == requests.codes.ok):
        click.secho(fileurl + 'HEAD failure :' + str(head_req.status_code),
                    fg='red')
        exit(1)
    else:
        return head_req


def do_fullGET(file_type, delivery, dir_target):
    """Download full file"""
    target = os.path.join(dir_target, basename(urlparse(delivery[file_type]).path))
    # store target in delivery
    delivery[file_type + "-cache"] = target
    get_req = requests.get(delivery[file_type])

    if not (get_req.status_code == requests.codes.ok):
        click.secho(file_type + ' HTTP GET failure :' + str(get_req.status_code),
                    fg='red')
    else:
        with open(target, 'wb') as target_file:
            target_file.write(get_req.content)
            import hashlib
            sha1Context = hashlib.sha1(get_req.content)
            delivery[file_type + "-sha1"] = sha1Context.hexdigest()
            target_file.close()
        return get_req


def checkSHA1(delivery):
    """Verify SHA1 values against computed ones."""
    mf = configparser.SafeConfigParser()
    mf.read_file(itertools.chain(['[MF]'], open(delivery["mf-cache"])))
    for name, value in mf.items('MF'):
        file_type = re.match('sha1\(.*\.(\w+)\)', name).group(1)
        if delivery[file_type + '-sha1']:
            if delivery[file_type + '-sha1'] == value:
                click.secho(name + ": verified.", fg='green')
            else:
                click.secho("{}: error({} != {} ).".format(name,
                                                           value,
                                                           delivery[file_type+'-sha1']),
                            fg='red')

                return False
    return True


def CheckDelivery(file_type, delivery):
    return checkURL(delivery[file_type])


def download_delivery(delivery, dir_target):
    """Downloads a template delivery set of files  from CDA with
    concurrent threads"""
    if not os.path.exists(dir_target):
        os.mkdir(dir_target)
    pp = pprint.PrettyPrinter(indent=4)
    CheckDelivery('txt', delivery)
    CheckDelivery('ovf', delivery)
    CheckDelivery('mf', delivery)
    workers = []
    delivery["vmdk-cache"] = []
    for vmdk_part in delivery['vmdk']:
        vmdk_head_req = checkURL(vmdk_part)
        vmdk_part_target = os.path.join(dir_target,
                                        basename(urlparse(vmdk_part).path))
        delivery["vmdk-cache"].append(vmdk_part_target)
        if 'content-length' in vmdk_head_req.headers:
            vmdk_size = int(vmdk_head_req.headers['content-length'])
        worker = Process(target=do_GET, args=(vmdk_part,
                                              vmdk_part_target,
                                              vmdk_size))
        workers.append(worker)
        worker.start()
    # Wait for all worker processes to finish
    txt_req = do_fullGET('txt', delivery, dir_target)
    do_fullGET('ovf', delivery, dir_target)
    do_fullGET('mf', delivery, dir_target)
    delivery['info'] = yaml.safe_load(txt_req.text)
    click.secho("Fetching {} / {}".format(delivery['info']['OTEC'],
                                          delivery['info']['template']['name']),
                fg='blue')
    for worker in workers:
        worker.join()
    vmdk_file_name = os.path.splitext(delivery["vmdk-cache"][0])[0]
    vmdk_file = open(vmdk_file_name, 'wb')
    vmdk_file.truncate()
    sha1whole = hashlib.sha1()
    for vmdk_cache_part in delivery["vmdk-cache"]:
        blksize = HTTP_CHUNKED_SIZE * 32
        sha1Context = hashlib.sha1()
        pp.pprint(vmdk_cache_part)
        with open(vmdk_cache_part, 'rb') as vmdk:
            chunk = vmdk.read(blksize)
            vmdk_file.write(chunk)
            while len(chunk) > 0:
                sha1Context.update(chunk)
                sha1whole.update(chunk)
                chunk = vmdk.read(blksize)
        ext = basename(vmdk_cache_part).split('.')[-1]
        delivery[ext + '-sha1'] = sha1Context.hexdigest()
    delivery['vmdk-sha1'] = sha1whole.hexdigest()
    delivery["vmdk-cache"] = vmdk_file_name
    vmdk_file.close()
    return checkSHA1(delivery)
