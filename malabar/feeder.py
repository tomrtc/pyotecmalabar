#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import gruvi

import click
import feedparser
import time
import os

def check_delivery(name,db):
        '''check availbal delivery'''
        with open(db, 'r') as database:
                for line in database:
                        if name in line:
                                return True
                        return False

def store_delivery_db(name,item,db):
        '''check availbal delivery'''
        with open(db, 'a') as database:
                current_limit= round(time.time() * 1000)
                if not check_delivery(name, db):
                        database.write(name + "/" + item + "/"+ str(current_limit) + "\n")


def check_outdated_delivery(name,db):
        '''remembering past delivery  soso implementation'''
        with open(db, 'r') as database:
                current_limit= round(time.time() * 1000)
                tolerance = 360
                for line in database:
                        if name in line:
                                old_limit_as_string = line.split('/', 2)[2]
                                old_limit = int(old_limit_as_string)
                                if current_limit - old_limit > tolerance:
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
        if check_outdated_delivery(post.title, rss_db):
                posts_to_skip.append(post.title)
                click.secho(post.title, fg='magenta')
        else:
                posts_to_print.append(post.title)
                click.secho(post.title, fg='yellow')
    for item in posts_to_print:
            if name in item:
                    click.secho(name + ' ⇒❯ ' + item, fg='cyan', blink=True)
                    store_delivery_db(name,item, rss_db)
                    break


# limit =
# import time
# from subprocess import check_output
# import sys
# #
# # function to get the current time
# #




# # return true if the title is in the database with a timestamp > limit
#
# #
#

# #
# # figure out which posts to print
# #
#

# #
# # add all the posts we're going to print to the database with the current timestamp
# # (but only if they're not already in there)
# #
#

# #
# # output all of the new posts
# #
# count = 1
# blockcount = 1
#
#     if count % 5 == 1:
#         print("\n" + time.strftime("%a, %b %d %I:%M %p") + '  ((( ' + feed_name + ' - ' + str(blockcount) + ' )))')
#         print("-----------------------------------------\n")
#         blockcount += 1
#     print(title + "\n")
#     count += 1
