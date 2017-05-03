# coding=utf-8

import redis
import pymongo

r = redis.Redis()
db = pymongo.MongoClient().faxin

def send():
    # docs = (x.get('doc_id') for x in db.find({'main_title': {'$exists': False}})[:51200])
    # for x in docs:
        # r.lpush('court:start_urls', x)
    r.lpush('court:start_urls', 'http://wenshu.court.gov.cn/')

send()
