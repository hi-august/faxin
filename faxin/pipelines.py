# -*- coding: utf-8 -*-

import pymongo
import pdb
from scrapy.conf import settings
import os
from scrapy.dupefilters import RFPDupeFilter
# from items import InformationItem, TweetsItem
import pdb


class MongoDBPipleline(object):
    def __init__(self):
        db = pymongo.MongoClient(settings['MONGODB_URL']).faxin
        self.court= db["court"]
        pdb.set_trace()
        # self.court.save({'test': 'test'})}

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        pass
        # if isinstance(item, InformationItem):
            # try:
                # self.Information.insert(dict(item))
            # except Exception:
                # pass
        # elif isinstance(item, TweetsItem):
            # try:
                # self.Tweets.insert(dict(item))
            # except Exception:
                # pass
        # return item


