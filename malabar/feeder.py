#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import gruvi

import click
import feedparser
import time
import os
from time import mktime
from datetime import datetime
from string import Template

def check_delivery(name,db):
        '''check availbal delivery'''
        with open(db, 'r') as database:
                for line in database:
                        if name in line:
                                return True
                        return False

def store_delivery_db(name,item,db, ts):
        '''check availbal delivery'''
        with open(db, 'a') as database:
                if not check_delivery(name, db):
                        database.write(name + "/" + item + "/"+ str(ts) + "\n")


def check_outdated_delivery(name,db, ts):
        '''remembering past delivery  soso implementation'''
        with open(db, 'r') as database:
                current_limit= int(time.time())
                tolerance = 360
                for line in database:
                        if name in line:
                                old_limit_as_string = line.split('/', 2)[2]
                                old_limit = int(old_limit_as_string)
                                if ts - old_limit > tolerance:
                                        return True
                                return False


def fetch_ovf_from_rss(name, rss_uri, rss_db):
    '''feedparsing and http-download'''
    click.secho(rss_uri, fg='green')
    if not os.path.isfile(rss_db):
            with open(rss_db, 'wt') as database:
                    database.write("# Hello this is a cache for OT.EC malabar!\n")
    # From template factory rss use feedparser
    feed = feedparser.parse(rss_uri)
    posts_to_print = []
    posts_to_skip = []
    for post in feed.entries:
        ts = int(mktime(post.published_parsed))
        if not name +'-' in post.title: #check_outdated_delivery(post.title, rss_db, ts):
                posts_to_skip.append(post)
                click.secho(post.title, fg='white')
        else:
                dt = datetime.fromtimestamp(ts)
                posts_to_print.append(post)
                click.secho(post.title + " <" + dt.isoformat() + ">", fg='yellow')

    for item in posts_to_print:
        ts = int(mktime(item.published_parsed))
        if name in item.title:
                dt = datetime.fromtimestamp(ts)
                decompose_id = item.title.split(' ')[1]
                click.secho(name + ' ⇒❯ ' + decompose_id + " <" + dt.isoformat() + ">" , fg='cyan', blink=True)
                store_delivery_db(name, decompose_id, rss_db, ts)
