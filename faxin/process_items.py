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
faxin = MongoClient(MONGODB_URL).faxin.faxin
faxin_param = MongoClient(MONGODB_URL).faxin.faxin_param

r = grs(REDIS_URL)

def send_faxin_gid():
    # docs = (x.get('doc_id') for x in db.find({'main_title': {'$exists': False}})[:51200])
    # for x in docs:
        # r.lpush('court:start_urls', x)
    print('start faxin gid')
    sort = [('update', 1)]
    for p in faxin.find({'finished': {'$exists': False}})[1: 300]:
        print('send to redis %s' %p.get('gid', ''))
        data = {'gid': p.get('gid', ''), 'url': p.get('url', '')}
        r.lpush('faxin:start_urls', json.dumps(data))

def send_faxin():
    for x in req_info:
        try:
            key = x['url'] + '|' + str(x.get('libid', ''))
            category_id = md5(key)
            t = faxin_param.find_one({'category_id': category_id})
            if t:
                page = t.get('page', [])
                pages = range(1, t.get('pages', 1)+1)
                unfinished = list(set(pages) - set(page))
                if unfinished:
                    data = {'info': x, 'page': list(unfinished)}
                    data = json.dumps(data)
                    r.lpush('faxin:start_urls', data)
                    logger.info('faxin send to redis %s' % data)
                else:
                    data = {'info': x, 'page': pages}
                    data = json.dumps(data)
                    r.lpush('faxin:start_urls', data)
                    logger.info('faxin send to redis %s' % data)

        except Exception as e:
            print(e)

# send_faxin()

def send_court():
    # docs = (x.get('doc_id') for x in db.find({'main_title': {'$exists': False}})[:51200])
    # for x in docs:
        # r.lpush('court:start_urls', x)
    print('start court')
    sort = [('update', 1)]
    for p in court.find({'finished': {'$exists': False}})[1: 300]:
        print('send to redis %s' %p.get('doc_id', ''))
        data = {'doc_id': p.get('doc_id', '')}
        r.lpush('court:start_urls', json.dumps(data))

# send_court()

def send():
    query = {
        'finished': {'$nin': [11, 1]},
        'pages': {'$lte': 100},
        #  'new3': 1,
    }
    # sort = [('update', 1)]
    #  pdb.set_trace()
    for p in param.find(query)[1: 10000]:
        page = p.get('page', [])
        if p.get('pages', 1) > 100:
            continue
        if page:
            all_page = range(1, p.get('pages', 1)+1)
            unfinished = list(set(all_page) - set(page))
            if not unfinished:
                param.update_one(
                    {'param': p.get('param')},
                    {'$set': {'finished': 1}},
                    upsert=False,
                )
            else:
                data = {'param': p.get('param', ''), 'page': unfinished, 'pages': p.get('pages', 1)}
                data = json.dumps(data)
                logger.info('send to redis %s' % data)
                r.lpush('court:start_urls', data)
        else:
            data = {'param': p.get('param', '')}
            data = json.dumps(data)
            logger.info('send to redis %s' % data)
            r.lpush('court:start_urls', data)
        data = {'param': p.get('param', '')}
        data = json.dumps(data)
        logger.info('send to redis %s' % data)
        r.lpush('court:start_urls', data)
        #  print(p)
        # p = {
            # 'param': u'文书类型:判决书,一级案由:民事案由,关键词:合同,中级法院:北京市第一中级人民法院,二级案由:人格权纠纷',
            # 'page': 2,
        # }

# send()

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
            if source == 'court:items':
                if item.get('finished', '') and item.get('doc_id', ''):
                    logger.info('get doc_id: %s', item.get('doc_id'))
                    court.update_one(
                        {'doc_id': item['doc_id']},
                        {'$set': item},
                        # upsert=True,
                    )
                    logger.debug("[%s ==> %s] Processing doc_id: %s", source, 'court', item.get('doc_id'))
                if not item.get('big', ''):
                    logger.debug("[%s ==> %s] Processing param: %s count: %s, pages: %s", source, 'court',
                                 item.get('param'), len(item.get('item_list')), item.get('pages'))
                    if item.get('item_list', []):
                        for x in item.get('item_list', []):
                            court.update_one(
                                {'doc_id': x['doc_id']},
                                {'$set': x},
                                 upsert=True,
                            )
                            logger.debug("[%s ==> %s] Processing doc_id: count: %s", source, 'court', x['doc_id'])
                        t = param.find_one({'param': item.get('param')})
                        if t:
                            page = t.get('page', [])
                            if int(item.get('page')) not in page:
                                page.append(int(item.get('page', '')))
                            # 这里可能有些数据没有抓去到
                            # 更新page数据
                            if len(set(page)) == x.get('pages', 1):
                                new = {'finished': 1, 'pages': item.get('pages', ''), 'page': page, 'update': int(time.time())}
                            else:
                                new = {'pages': item.get('pages', ''), 'page': page, 'update': int(time.time())}
                            param.update_one(
                                {'param': item.get('param')},
                                {'$set': new},
                                upsert=False,
                            )
                            logger.debug("[%s ==> %s] Processing param: %s", source, 'court_param', item.get('param'))
                    else:
                        t = param.find_one({'param': item.get('param')})
                        new = {'pages': item.get('pages', ''), 'finished': 11}
                        param.update_one(
                            {'param': item.get('param')},
                            {'$set': new},
                            upsert=False,
                        )
                        pass
                else:
                    t = param.find_one({'param': item.get('param')})
                    if t:
                        new = {'pages': item.get('pages', ''), 'update': int(time.time())}
                        param.update_one(
                            {'param': item.get('param')},
                            {'$set': new},
                            upsert=False,
                        )
                        # pdb.set_trace()
                        logger.debug("[%s ==> %s] Processing param: %s pages: %s", source, 'court_param',
                                     item.get('param'), item.get('pages'))

            elif source == 'faxin:items':
                if item.get('gid', ''):
                    logger.info('get gid: %s', item.get('gid'))
                    # pdb.set_trace()
                    faxin.update_one(
                        {'gid': item['gid']},
                        {'$set': item},
                        # upsert=True,
                    )
                    logger.debug("[%s ==> %s] Processing gid: %s", source, 'court', item.get('gid'))
                # if item.get('item_list', []) and item.get('category_id', ''):
                    # logger.debug("[%s ==> %s] Processing category_id: %s count: %s", source, 'faxin', item['category_id'], len(item['item_list']))
                    # for x in item.get('item_list', ''):
                        # faxin.update_one({'link_id': x['link_id']}, {'$set': x}, upsert=True)
                        # logger.debug("[%s ==> %s] Processing link_id : %s", source, 'faxin', x['link_id'])
                    # t = faxin_param.find_one({'category_id': item.get('category_id', '')})
                    # # pdb.set_trace()
                    # new = {}
                    # if t:
                        # page = t.get('page', [])
                        # if item['page'] not in page:
                            # page.append(item['page'])
                        # if len(page) == t.get('pages', 1):
                            # new = {
                            # 'finished': 1,'page': page, 'update': int(time.time()),
                            # }
                            # faxin_param.update_one(
                                # {'category_id': item['category_id']},
                                # {'$set': new},
                                # upsert=False,
                            # )
                            # logger.debug("[%s ==> %s] Processing category_id: count: %s", source, 'court', item['category_id'])
                        # else:
                            # new = {'page': page, 'update': int(time.time())}
                            # faxin_param.update_one(
                                # {'category_id': item['category_id']},
                                # {'$set': new},
                                # upsert=False,
                            # )
                            # logger.debug("[%s ==> %s] Processing category_id: count: %s", source, 'court', item['category_id'])
        except KeyError:
            logger.exception("[%s] Failed to process item:\n%r",
                             source, pprint.pformat(item))
            continue

        processed += 1
        if processed % log_every == 0:
            logger.info("Processed %s items", processed)


def main(key):
    # parser = argparse.ArgumentParser(description=__doc__)
    # parser.add_argument('key', help="Redis key where items are stored")
    # parser.add_argument('--host')
    # parser.add_argument('--port')
    # parser.add_argument('--timeout', type=int, default=5)
    # parser.add_argument('--limit', type=int, default=0)
    # parser.add_argument('--progress-every', type=int, default=100)
    # parser.add_argument('-v', '--verbose', action='store_true')

    # args = parser.parse_args()

    params = {}
    # if args.host:
        # params['host'] = args.host
    # if args.port:
        # params['port'] = args.port

    params['port'] = REDIS_PORT
    params['host'] = REDIS_HOST
    # logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    #  r = get_redis(**params)
    # host = r.connection_pool.get_connection('info').host
    # logger.info("Waiting for items in '%s' (server: %s)", args.key, host)
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
        'court:items': 'court:start_urls',
        # 'faxin:items': 'faxin:start_urls',
    }
    while True:
        for k, v in item.items():
            check_redis_count = r.llen(v)
            print(' ==> redis-key remain: %s'%check_redis_count)
            if check_redis_count < 100:
                if v == 'court:start_urls':
                    send()
                elif v == 'faxin:start_urls':
                    send_faxin_gid()
            #  main(k)
            print(' ==> sleep 180 s')
            time.sleep(180)
