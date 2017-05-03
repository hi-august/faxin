# -*- coding: utf-8 -*-

import time
from screct import *

BOT_NAME = ['faxin', ]

SPIDER_MODULES = ['faxin.spiders']
NEWSPIDER_MODULE = 'faxin.spiders'

DOWNLOADER_MIDDLEWARES = {
    "faxin.middleware.UserAgentMiddleware": 401,
    "faxin.middleware.AbuYunProxyMiddleware": 301,
    'faxin.middleware.DBRetryMiddleware': 510, # 这个RetryMiddleware要大于默认的。
    # "faxin.middleware.CookiesMiddleware": 402,
}

ITEM_PIPELINES = {
     # "faxin.pipelines.MongoDBPipleline": 300,
    'scrapy_redis.pipelines.RedisPipeline': 400,
}


# DUPEFILTER_CLASS = None
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# DUPEFILTER_CLASS = 'scrapy.dupefilter.BaseDupeFilter'
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True

HTTPERROR_ALLOWED_CODES = [307,403, 404, 427, 500, 502, 504]

RETRY_TIMES = 3
# RETRY_HTTP_CODES = [500, 502, 503, 504, 408]
DB_RETRY_HTTP_CODES = [403, 404, 429, 302, 301]

# scrapy crawl douban -s LOG_FILE=/tmp/dmoz.log
#  fn = time.strftime('%Y-%m-%d|%H-%M-%S',time.localtime(time.time())) + '.log'
#  LOG_FILE='/tmp/faxin/logs/%s' %fn


CONCURRENT_REQUESTS=32

DOWNLOAD_DELAY=0.15
