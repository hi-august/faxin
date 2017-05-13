# -*- coding: utf-8 -*-
from scrapy import Request, FormRequest
from scrapy_redis.spiders import RedisSpider
import time
import json
import pdb
#  import re
from bs4 import BeautifulSoup as bs
import ipdb


class Court(RedisSpider):
    name = "court2"
    redis_key = "court2:start_urls"

    def __init__(self, *args, **kw):
        super(Court, self).__init__(*args, **kw)

    def deal_with_content(self, content):
        res = content.replace('\\', '').strip('\"')
        res = json.loads(res, strict=False)
        return res

    def make_requests_from_url(self, data):
        data = json.loads(data)
        if data.get('doc_id', ''):
            uri = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=%s#%s' %(data.get('doc_id', ''), time.time())
            print uri
            return Request(
                uri,
                method='get',
                meta={'data': data},
                callback=self.parse2,
            )

    def parse2(self, response):
        data = response.meta['data']
        body = response.body
        start = body.find('{\\')
        end = body.find('var jsonData') - 7
        soup = body[start: end]
        soup = self.deal_with_content(soup)
        Html = soup['Html']
        info = bs(Html, 'lxml')
        content = []
        for p in info.find_all('div'):
            tmp = '\n'.join(p.strings)
            if tmp.strip():
                content.append(tmp.strip())
        attrs = dict(
            content=content,
            finished=1,
            doc_id=data.get('doc_id', ''),
        )
        # pdb.set_trace()
        yield attrs

