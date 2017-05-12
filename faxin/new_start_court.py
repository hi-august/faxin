# coding=utf-8
"""A script to process items from a redis queue."""

from __future__ import print_function, unicode_literals

#  import argparse
import json
import logging
import pprint
#  import sys
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
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
import datetime
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
category = MongoClient(MONGODB_URL).faxin.court_category

r = grs(REDIS_URL)

def get_date():
    dates = []
    now = datetime.datetime.now()
    default_date = datetime.datetime(2013, 7, 1, 0, 0)
    query_date = datetime.timedelta(days=1) + default_date
    # 爬取10天之内数据
    # query_date = now + datetime.timedelta(days=-1)
    while query_date < now:
        start = query_date.strftime('%Y-%m-%d')
        query_date += datetime.timedelta(days=1)
        end = query_date.strftime('%Y-%m-%d')
        param = u'上传日期:%s TO %s'%(start, end)
        dates.append(param)
    return dates

def gen_new_param():
    dates = get_date()
    today = datetime.datetime.now().strftime('%Y%m%d')
    n = 1
    for x in dates:
        p = x
        t = param.find_one({'param': p.strip()})
        if not t:
            data = {today : n, 'param': p.strip(), 'type': ''}
            print('insert %s'%(p))
            param.update_one({'param': p.strip()}, {'$set': data}, upsert=True)
        #  for y in [u'刑事案件', u'行政案件', u'赔偿案件', u'执行案件']:
            #  if x:
                #  p = u'%s文书类型:判决书,案件类型:%s'%(x,y)
                #  t = param.find_one({'param': p.strip()})
                #  if not t:
                    #  data = {today : n, 'param': p.strip(), 'type': y}
                    #  print('insert %s'%(p))
                    #  param.update_one({'param': p.strip()}, {'$set': data}, upsert=True)

# gen_new_param()
def gen_new_start_param(pp, info):
    today = datetime.datetime.now().strftime('%Y%m%d')
    source_type = pp.get('type', '')
    p = pp['param']
    if u'案件类型' not in p:
        for y in [u'刑事案件', u'行政案件', u'赔偿案件', u'执行案件']:
            new_p = u'%s,案件类型:%s'%(p,y)
            t = param.find_one({'param': new_p.strip()})
            if not t:
                data = {today : today, 'param': new_p.strip(), 'type': y}
                print('insert %s'%(p))
                param.update_one({'param': p.strip()}, {'$set': data}, upsert=True)
    if u'裁判年份' not in p:
        for zz in info['裁判年份'.decode('utf-8')]:
            if zz:
                new_p = u'%s,%s:%s'%(p, '裁判年份'.decode('utf-8'), zz)
                data = {today: 1, 'param': new_p.strip(), 'type': source_type}
                param.update_one({'param': new_p.strip()}, {'$set': data}, upsert=True)
    elif u'法院地域' not in p:
        for a in info['法院地域'.decode('utf-8')]:
            if a:
                new_p = u'%s,%s:%s'%(p, '法院地域'.decode('utf-8'), a)
                data = {today: 1, 'param': new_p.strip(), 'type': source_type}
                param.update_one({'param': new_p.strip()}, {'$set': data}, upsert=True)
    elif u'关键词' not in p:
        for a in info['关键词'.decode('utf-8')]:
            if a:
                new_p = u'%s,%s:%s'%(p, '关键词'.decode('utf-8'), a)
                data = {today: 1, 'param': new_p.strip(), 'type': source_type}
                param.update_one({'param': new_p.strip()}, {'$set': data}, upsert=True)
    # elif u'法院层级' not in p:
        # for a in info[u'法院层级']:
            # if a:
                # new_p = '%s,法院层级:%s'(p, a)
                # data = {today: 1, 'param': p.strip()}
                # param.update_one({'param': new_p}, {'$set': data}, upsert=True)
    elif u'一级案由' not in p:
        for a in info['一级案由'.decode('utf-8')]:
            if a:
                new_p = u'%s,一级案由:%s'%(p, a)
                data = {today: 1, 'param': new_p.strip(), 'type': source_type}
                param.update_one({'param': new_p.strip()}, {'$set': data}, upsert=True)
    elif u'审判程序' not in p:
        for a in info['审判程序'.decode('utf-8')]:
            if a:
                new_p = u'%s,审判程序:%s'%(p, a)
                data = {today: 1, 'param': new_p.strip(), 'type': source_type}
                param.update_one({'param': new_p.strip()}, {'$set': data}, upsert=True)
    elif u'二级案由' not in p:
        info2 = category.find_one({u'二级案由': {'$exists': True}, 'type': source_type})
        for a in info2['二级案由'.decode('utf-8')]:
            if a:
                new_p = u'%s,二级案由:%s'%(p, a)
                data = {today: 1, 'param': new_p.strip(), 'type': source_type}
                param.update_one({'param': new_p.strip()}, {'$set': data}, upsert=True)
    elif u'中级法院' not in p:
        info2 = category.find({u'中级法院': {'$exists': True}})
        courts = []
        for b in info2:
            for c in b['中级法院'.decode('utf-8')]:
                courts.append((c, b['root']))
        courts = list(set(courts))
        for a in courts:
            if a:
                if a[1] not in p:
                    new_p = u'%s,中级法院:%s'%(p, a[0])
                    data = {today: 1, 'param': new_p.strip(), 'type': source_type}
                    param.update_one({'param': new_p.strip()}, {'$set': data}, upsert=True)
    elif u'三级案由' not in p:
        info2 = category.find({u'三级案由': {'$exists': True}, 'type': source_type})
        courts = []
        for b in info2:
            for c in b['三级案由'.decode('utf-8')]:
                courts.append((c, b['root']))
        courts = list(set(courts))
        for a in courts:
            if a:
                if a[1] not in p:
                    new_p = u'%s,三级案由:%s'%(p, a[0])
                    data = {today: 1, 'param': new_p.strip(), 'type': source_type}
                    param.update_one({'param': new_p.strip()}, {'$set': data}, upsert=True)
    # elif u'四级案由' not in p:
        # info2 = category.find({u'四级案由': {'$exists': True}})
        # courts = []
        # for b in info2:
            # for c in b['四级案由'.decode('utf-8')]:
                # courts.append((c, b['root']))
        # courts = list(set(courts))
        # for a in courts:
            # if a:
                # if a[1] not in p:
                    # new_p = u'%s,四级案由:%s'%(p, a)
                    # data = {today: 1, 'param': new_p.strip(), 'type': source_type}
                    # param.update_one({'param': new_p.strip()}, {'$set': data}, upsert=True)
    elif u'基层法院' not in p:
        info2 = category.find({u'基层法院': {'$exists': True}})
        courts = []
        for b in info2:
            for c in b['基层法院'.decode('utf-8')]:
                courts.append((c, b['root']))
        courts = list(set(courts))
        for a in courts:
            if a:
                if a[1] not in p:
                    new_p = u'%s,基层法院:%s'%(p, a[0])
                    data = {today: 1, 'param': new_p.strip(), 'type': source_type}
                    param.update_one({'param': new_p.strip()}, {'$set': data}, upsert=True)

def send_court():
    print('start send_court ...')
    query = {
        'param': {'$regex': '上传日期'},
        'finished': {'$nin': [11, 1]},
        # 'finished': {'$exists': False},
        # 'pages': {'$lte': 100},
    }
    if param.find(query).count() == 0:
        pass
    gen_new_param()
        #  return
    for p in param.find(query):
        page = p.get('page', [])
        if p.get('pages', 1) > 100:
            if u'上传日期' in p.get('param', ''):
                if p['type']:
                    info = category.find_one({u'文书类型': {'$exists': True}, 'type': p['type']})
                else:
                    info = category.find_one({u'文书类型': {'$exists': True}})
                print(p)
                gen_new_start_param(p, info)
            continue
        if u'上传日期' not in p.get('param', ''):
            continue
        if u'一级案由:民事案由' in p.get('param', ''):
            continue
        if u'案件类型:民事案件' in p.get('param', ''):
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
                data = {'param': p.get('param', ''), 'page': unfinished, 'pages': p.get('pages', 1), 'type': p['type']}
                data = json.dumps(data)
                logger.info('send to redis %s' % data)
                r.lpush('court:start_urls', data)
        else:
            data = {'param': p.get('param', ''), 'type': p['type']}
            data = json.dumps(data)
            logger.info('send to redis %s' % data)
            r.lpush('court:start_urls', data)
        data = {'param': p.get('param', ''), 'type': p['type']}
        data = json.dumps(data)
        logger.info('send to redis %s' % data)
        r.lpush('court:start_urls', data)

def send_court_doc():
    print('start court doc_id ...')
    query = {'finished': {'$exists': False}}
    cnt = 0
    for p in court.find(query)[:20000]:
        print('send to redis %s' %p.get('doc_id', ''))
        data = {'doc_id': p.get('doc_id', '')}
        r.lpush('court:start_urls', json.dumps(data))
        cnt += 1
        court.update_one({'doc_id': p.get('doc_id', '')}, {'$set': {'update_time': int(time.time())}})
    return cnt


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
                            # print('send to redis %s' %x.get('doc_id', ''))
                            # data = {'doc_id': x.get('doc_id', '')}
                            # r.lpush('court:start_urls', json.dumps(data))
                            # court.update_one({'doc_id': x.get('doc_id', '')}, {'$set': {'update_time': int(time.time())}})
                            logger.debug("[%s ==> %s] Processing doc_id: count: %s", source, 'court', x['doc_id'])
                        t = param.find_one({'param': item.get('param')})
                        if t:
                            page = t.get('page', [])
                            if int(item.get('page')) not in page:
                                page.append(int(item.get('page', '')))
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
                else:
                    p = item.get('param')
                    t = param.find_one({'param': p})
                    if t:
                        new = {'pages': item.get('pages', ''), 'update': int(time.time()), 'finished': 0}
                        param.update_one(
                            {'param': item.get('param')},
                            {'$set': new},
                            upsert=False,
                        )
                        logger.debug("[%s ==> %s] Processing param: %s pages: %s", source, 'court_param',
                                     item.get('param'), item.get('pages'))
                    if int(item.get('pages', '')) > 100:
                        if item['type']:
                            info = category.find_one({u'文书类型': {'$exists': True}, 'type': item['type']})
                        else:
                            info = category.find_one({u'文书类型': {'$exists': True}})
                            #  pdb.set_trace()
                        print('start to deal with more 100')
                        gen_new_start_param(item, info)
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
        'court:items': 'court:start_urls',
    }
    while True:
        for k, v in item.items():
            check_redis_count = r.llen(v)
            if 'court:requests' in r.keys():
                r.delete('court:requests')
            if 'court2:requests' in r.keys():
                r.delete('court2:requests')
            if 'court:dupefilter' in r.keys():
                r.delete('court:dupefilter')
            if 'court2:dupefilter' in r.keys():
                r.delete('court2:dupefilter')
            print(' ==> redis-key remain: %s'%check_redis_count)
            if check_redis_count < 100:
                send_court()
            # main(k)
            print(' ==> sleep 180 s')
            time.sleep(180)
