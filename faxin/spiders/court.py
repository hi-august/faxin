# -*- coding: utf-8 -*-
from scrapy import Request, FormRequest
from scrapy_redis.spiders import RedisSpider
import time
import json
import pdb
#  import re
from bs4 import BeautifulSoup as bs


class Court(RedisSpider):
    name = "court"
    redis_key = "court:start_urls"

    def __init__(self, *args, **kw):
        super(Court, self).__init__(*args, **kw)

    def deal_with_content(self, content):
        res = content.replace('\\', '').strip('\"')
        res = json.loads(res)
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
        param = {
             'Direction': 'asc',
             'Index': '0',
             'Order': u'法院层级',
             'Page': '20',
             'Param': data.get('param', ''),
        }
        uri = 'http://wenshu.court.gov.cn/List/ListContent#%s'%time.time()
        if data.get('page', []):
            for x in data['page']:
                param['Index'] = str(x)
                return FormRequest(
                    uri,
                    method='post',
                    formdata=param,
                    meta={'param': param},
                    callback=self.parse_get_item,
                    dont_filter=True,
                )

        if u'文书类型' in data.get('param', ''):
            return FormRequest(
                uri,
                method='post',
                formdata=param,
                # body=json.dumps(data),
                meta={'param': param, 'type': p['type']},
                callback=self.check_item_count,
                dont_filter=True,
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
        yield attrs

    def check_item_count(self, response):
        try:
            param = response.meta['param']
            source_type= response.meta['type']
            try:
                res = self.deal_with_content(response.body)
                total = res[0]['Count']
            except Exception as e:
                #  total = 0
                print(e)
                self.logger.info('[check_item_count]%s ==> %s', json.dumps(param), e)
            pages = int(round(int(total)/20.0))
            if pages == 0:
                pages = 1
            if pages > 100:
                # pdb.set_trace()
                yield {'big': True, 'page': [], 'pages': pages, 'param': param['Param'], 'item_list': [], 'type': source_type}
                return
            if 1 <= pages <= 100:
                for page in range(1, pages+1):
                    uri = 'http://wenshu.court.gov.cn/List/ListContent?%s'%time.time()
                    #  pdb.set_trace()
                    param['Index'] = str(page)
                    yield FormRequest(
                        uri,
                        method='post',
                        formdata=param,
                        meta={'param': param, 'type': source_type},
                        callback=self.parse_get_item,
                        dont_filter=True,
                    )
        except Exception as e:
            print(e)
            self.logger.info('[check_item_count] %s ==> %s', json.dumps(param), e)

    def parse_get_item(self, response):
        try:
            param = response.meta['param']
            source_type= response.meta['type']
            res = self.deal_with_content(response.body)
            total = res[0]['Count']
            pages = int(round(int(total)/20.0))
            if pages == 0:
                pages = 1
            info = res[1:]
            tmp = []
            for x in info:
                doc_id = x.get(u'文书ID', '')
                try:
                    pub_date_sort = int(x.get(u'裁判日期', '').replace('-', ''))
                except Exception as e:
                    pub_date_sort = 0
                    self.logger.info('[parse_get_item] %s ==> %s', doc_id, e)
                attrs = dict(
                case_name = x.get(u'案件名称', ''),
                pub_date = x.get(u'裁判日期', ''),
                case_raw = x.get(u'裁判要旨段原文', ''),
                case_id = x.get(u'案号', ''),
                doc_id = doc_id,
                court_proceeding= x.get(u'审判程序', ''),
                court_name= x.get(u'法院名称', ''),
                reason = x.get(u'不公开理由', ''),
                case_type = x.get(u'案件类型', ''),
                total=total,
                pub_date_sort = pub_date_sort,
                )
                tmp.append(attrs)
                # yield attrs
            yield {
                'big': False,
                'page': param['Index'],
                'pages': pages,
                'param': param['Param'],
                'item_list': tmp,
                'type': source_type,
            }
        except Exception as e:
            print(e)
            self.logger.info('[parse_get_item] %s ==> %s', json.dumps(param), e)
