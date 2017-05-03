#!/usr/bin/env python
# coding=utf-8
"""A script to process items from a redis queue."""

from __future__ import print_function, unicode_literals

#  import argparse
import json
import logging
import pprint
#  import sys
import time
from gevent import monkey
monkey.patch_all()
from pymongo import MongoClient
from settings import MONGODB_URL, REDIS_HOST, REDIS_URL, REDIS_PORT

from utils import get_redis as grs
from utils import md5
from logging import Formatter, StreamHandler, FileHandler
from instance import faxin_req_info as req_info
import pdb

import signal
def graceful_reload(signum, traceback):
    """Explicitly close some global MongoClient object."""
    court.close()
    signal.signal(signal.SIGHUP, graceful_reload)

fmt = Formatter('[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger('process_items')
fhd = logging.FileHandler('process_items.log')
fhd.setFormatter(fmt)
logger.addHandler(fhd)
logger.setLevel(logging.DEBUG)
stdout_hd = logging.StreamHandler()
stdout_hd.setFormatter(fmt)
logger.addHandler(stdout_hd)
logger.setLevel(logging.DEBUG)

court = MongoClient(MONGODB_URL).faxin.court
param = MongoClient(MONGODB_URL).faxin.court_param
#  faxin = MongoClient(MONGODB_URL).faxin.faxin
faxin = MongoClient(MONGODB_URL).faxin.faxin_new
faxin_param = MongoClient(MONGODB_URL).faxin.faxin_param

r = grs(REDIS_URL)

def send_faxin_gid():
    print('start faxin gid ...')
    query = {'finished': {'$exists': False}}
    #  query = {}
    for p in faxin.find(query)[:10000]:
        print('send to redis %s' %p.get('gid', ''))
        data = {'gid': p.get('gid', ''), 'url': p.get('url', '')}
        r.lpush('faxin:start_urls', json.dumps(data))
        faxin.update_one({'gid': p.get('gid', '')}, {'$set': {'update_time': int(time.time())}})

def process_items(r, keys, timeout, limit=0, log_every=1000, wait=.1):
    limit = limit or float('inf')
    processed = 0
    print('starting process_items ...')
    while processed < limit:
        # Change ``blpop`` to ``brpop`` to process as LIFO.
        ret = r.blpop(keys, timeout)
        # If data is found before the timeout then we consider we are done.
        if ret is None:
            time.sleep(wait)
            continue

        source, data = ret
        try:
            item = json.loads(data)
        except Exception:
            logger.exception("Failed to load item:\n%r", pprint.pformat(data))
            continue

        try:
            if source == 'faxin:items':
                if item.get('gid', ''):
                    logger.info('get gid: %s', item.get('gid'))
                    # pdb.set_trace()
                    faxin.update_one(
                        {'gid': item['gid']},
                        {'$set': item},
                        # upsert=True,
                    )
                    logger.debug("[%s ==> %s] Processing gid: %s", source, 'court', item.get('gid'))
        except KeyError:
            logger.exception("[%s] Failed to process item:\n%r",
                             source, pprint.pformat(item))
            continue

        processed += 1
        if processed % log_every == 0:
            logger.info("Processed %s items", processed)


def main(key):
    params = {}
    params['port'] = REDIS_PORT
    params['host'] = REDIS_HOST
    kwargs = {
        'keys': key,
        'timeout': 5,
        'limit': 0,
        'log_every': 100,
    }
    try:
        process_items(r, **kwargs)
        retcode = 0  # ok
    except KeyboardInterrupt:
        retcode = 0  # ok
    except Exception:
        # logger.exception("Unhandled exception")
        retcode = 2

    return retcode


if __name__ == '__main__':
    item = {
        'faxin:items': 'faxin:start_urls',
    }
    while True:
        for k, v in item.items():
            check_redis_count = r.llen(v)
            print(' ==> redis-key remain: %s'%check_redis_count)
            #  if check_redis_count < 100:
                #  if v == 'court:start_urls':
                    #  send_court()
                #  elif v == 'faxin:start_urls':
                    #  send_faxin_gid()
            main(k)
            print(' ==> sleep 180 s')
            time.sleep(180)
