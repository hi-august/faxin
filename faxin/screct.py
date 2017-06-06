# coding=utf-8

import os

PROXY_URL = "http://proxy.abuyun.com:9020"
PROXY_USERINFO = "H9IN46JH29Z543XD:87D004203561FB19"
MONGODB_URL = 'mongodb://august:nana@114.215.148.175:27019/admin?authMechanism=SCRAM-SHA-1'

REDIS_URL = "redis://:august, nana@114.215.148.175:6379"
REDIS_HOST = '114.215.148.175'
REDIS_PORT = 6379
REDIS_PASS = 'august, nana'
if os.getenv('server', '') == 'test':
    #  print(os.getenv('server', ''))
    MONGODB_URL = 'mongodb://127.0.0.1:27017/'
    #  REDIS_URL = "redis://127.0.0.1:6379"
    REDIS_PASS = None
    REDIS_URL = None
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
