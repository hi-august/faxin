# -*- coding: utf-8 -*-
from scrapy import Request, FormRequest
from scrapy_redis.spiders import RedisSpider
import time
import json
import pdb
import re
#  from scrapy.conf import settings
from bs4 import BeautifulSoup as bs
from scrapy.shell import inspect_response
#  from faxin.utils import md5
import os
import sys
import ipdb
path = os.path.abspath(os.getcwd())
print(path)
sys.path.append(path)
#  from utils import md5


class Faxin(RedisSpider):
    name = 'faxin'
    redis_key = 'faxin:start_urls'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'faxin.middleware.CookiesMiddleware': 402,
            'faxin.middleware.DBRetryMiddleware': 301,
        },
        'DOWNLOAD_DELAY': 1.15,
    }

    def __init__(self, *args, **kw):
        super(Faxin, self).__init__(*args, **kw)

    def get_gid(self, url):
        gid = re.search(r'gid=\S+&', url)
        if gid:
            gid  = gid.group(0)[4:-1]
            return gid
        else:
            gid = re.search(r'gid=\S+', url)
            if gid:
                gid  = gid.group(0)[4:]
                return gid
            else:
                pdb.set_trace()

    def make_requests_from_url(self, data):
        data = json.loads(data)
        # if data.get('page', []):
            # body = data['info']['param']
            # for x in data['page']:
                # for a, b in data.items():
                    # if 'Page' in a:
                        # body[a] = str(x)
                # return FormRequest(
                    # data['info']['url'],
                    # method='post',
                    # formdata=json.loads(body),
                    # meta={'data': data, 'page': x},
                    # callback=self.parse_get_item,
                    # dont_filter=True,
                # )
        if data.get('gid', ''):
            return Request(
                data.get('url', '')+'#%d'%(int(time.time())),
                method='get',
                meta={'data': data, 'dont_redirect': True},
                callback=self.parse_item2,
            )
            pass

    def parse_item2(self, response):
        data = response.meta['data']
        soup = bs(response.body, 'lxml')
        law_title = soup.find('div', attrs={'class': 'law-title'})
        title_m = soup.find('div', attrs={'class': 'title_m'})
        info = soup.find_all('div', attrs={'class': 'naturePop'})
        info2 = soup.find('div', attrs={'class': 'fulltext'})
        quotes = soup.find('div', attrs={'class', 'title_s'})
        if not info2:
            info2 = soup.find('div', attrs={'class': 'content_bg'})
        if title_m:
            title_m = title_m.text.strip()
        else:
            title_m = ''
        if law_title:
            law_title= law_title.text.strip()
        else:
            law_title = ''
        if u'您的访问频率过快，请稍后刷新' in soup.text:
            time.sleep(3)
            yield Request(
                data.get('url', '')+'#%d'%(int(time.time())),
                method='get',
                meta={'data': data},
                callback=self.parse_item2,
            )
            return
        content = []
        for y in info2.strings:
            if y.strip():
                content.append(y.strip())
        #  content = []
        legal_history = []
        attr_tag = []
        for y in info:
            if y.find('div', attrs={'class': 'timeMod'}) and y.find('div', attrs={'class': 'time-p'}) and not y.find('div', attrs={'class': 'js_pop2'}):
                if '1982-02-15' in y.text:
                    continue
                #  ipdb.set_trace()
                for x in y.find_all('div', attrs={'class': 'clearfix'}):
                    try:
                        date = x.find('div', attrs={'class': 'time-t1'}).text.strip()
                    except:
                        date = ''
                    try:
                        name = x.find('div', attrs={'class': 'time-t3'}).text.strip()
                    except:
                        name = ''
                    tmp = {'date': date, 'name': name}
                    if tmp in legal_history:
                        continue
                    legal_history.append(tmp)
            elif y.find('div', attrs={'class': 'nat-listMod'}):
                for x in y.find_all('li', attrs={'class': 'clearfix'}):
                    try:
                        name = x.text.split()[0].strip()
                    except:
                        name = ''
                    try:
                        value = x.text.split()[1].strip()
                    except:
                        value = ''
                    tmp = {'name': name,'value': value}
                    if tmp in attr_tag:
                        continue
                    attr_tag.append(tmp)
        if soup.find('div', attrs={'class': 'content_bg'}):
            for x in soup.find('ul', attrs={'class': 'attribute_listview'}).find_all('li', attrs={'class': 'attribute_listview_item'}):
                try:
                    name = x.text.split()[0].strip()
                except:
                    name = ''
                try:
                    value = x.text.split()[1].strip()
                except:
                    value = ''
                tmp = {'name': name,'value': value}
                if tmp in attr_tag:
                    continue
                attr_tag.append(tmp)
        quote = []
        if quotes:
            for i, y in enumerate(info2.find_all('a', attrs={'fid': True})):
                try:
                    #  ipdb.set_trace()
                    gid = y.get('fid', '')
                    name = y.text.strip()
                    tmp = {'gid': gid, 'name': name}
                    if tmp in quote:
                        continue
                    quote.append(tmp)
                except:
                    pass
        attrs = dict(
            law_title=law_title,
            title_m=title_m,
            content=content,
            attr_tag=attr_tag,
            legal_history=legal_history,
            quote=quote,
            url=data['url'],
            gid=data['gid'],
            finished=1,
        )
        yield attrs

    def parse_item(self, response):
        data = response.meta['data']
        gid = self.get_gid(data['url'])
        soup = bs(response.body, 'lxml')
        law_title = soup.find('div', attrs={'class': 'law-title'})
        title_m = soup.find('div', attrs={'class': 'title_m'})
        quotes = soup.find('div', attrs={'class', 'title_s'})
        content = soup.find('div', attrs={'class': 'fulltext'})
        if quotes:
            content.div.decompose()
        if title_m:
            title_m = title_m.text.strip()
            content.div.decompose()
        if law_title:
            law_title = law_title.text.strip()
        content = '|||'.join(content.strings)
        content = '|||'.join(content.split())
        content = re.sub(r'[\|]{3,}','|||', content)
        if content.startswith('|||'):
            content = content[3:]
        legal_history = []
        attr_tag = []
        info = soup.find_all('div', attrs={'class': 'naturePop'})
        for y in info:
            if y.find('div', attrs={'class': 'timeMod'}) and y.find('div', attrs={'class': 'time-p'}) and not y.find('div', attrs={'class': 'js_pop2'}):
                if not legal_history:
                    for x in y.find_all('div', attrs={'class': 'clearfix'}):
                        date = x.find('div', attrs={'class': 'time-t1'}).text
                        name = x.find('div', attrs={'class': 'time-t3'}).text
                        tmp = {'date': date, 'name': name}
                        if '1982-02-15' not in date:
                            legal_history.append(tmp)
            elif y.find('div', attrs={'class': 'nat-listMod'}):
                if not attr_tag:
                    for x in y.find_all('li', attrs={'class': 'clearfix'}):
                        try:
                            name = x.text.split()[0]
                        except:
                            name = ''
                        try:
                            value = x.text.split()[1]
                        except:
                            value = ''
                        tmp = {'name': name,'value': value}
                        attr_tag.append(tmp)
            for x in  '|'.join(y.strings).split('|'):
                if x.strip():
                    print x.strip()
        # http://www.faxin.cn/lib/zyfl/GetCommonData.ashx?gid=A191317&top=200&left=240&tiao=0
        quote = []
        if quotes:
            for i, y in enumerate(quotes.find_all('a', attrs={'fid': True})):
                gid = y.get('fid', '')
                name = y.text.strip()
                tmp = {'gid': gid, 'name': name}
                quote.append(tmp)
        attrs = dict(
            gid=gid,
            law_title=law_title,
            title_m=title_m,
            content=content,
            attr_tag=attr_tag,
            legal_history=legal_history,
            quote=quote,
        )
        yield attrs

    def parse_get_item(self, response):
        data = response.meta['data']['info']
        page = response.meta['page']
        body = response.body
        soup = bs(body.replace('\\', ''), 'lxml')
        pages = soup.find_all('a')[-1].get('onclick', '')
        pages = int(re.findall(r'\d+', pages)[-1])
        tmp = []
        for x in soup.find_all('div', attrs={'class': 'fz-title1'})[:50]:
            url = '/'.join(response.url.split('/')[:-1]) + '/' + x.find('a').get('href', '')
            link_id = md5(url)
            new = {
                'category': data['category'],
                'sub_category': data['sub_category'],
                'url': url, 'link_id': link_id}
            #  print(url, link_id)
            tmp.append(new)

        key = data['url'] + '|' + str(data.get('libid', 0))
        category_id = md5(key)
        #  inspect_response(response, self)
        return {'item_list': tmp, 'category_id': category_id, 'page': page}

        #  db.update_one({'link_id': link_id}, {'$set': new}, upsert=True)
        #  key = req['url'] + '|' + str(req.get('libid', 0))
        #  t = db2.find_one({'category_id': category_id})
        #  # pdb.set_trace()
        #  new = {}
        #  if t:
            #  page = t.get('page', [])
            #  if n not in page:
                #  page.append(n)
            #  if len(page) == x.get('pages', 1):
                #  new = {
                #  'category': req['category'],
                #  'sub_category': req['sub_category'],
                    #  'finished': 1, 'pages': pages, 'page': page, 'update': int(time.time())}
            #  else:
                #  new = {
                #  'category': req['category'],
                #  'sub_category': req['sub_category'],
                    #  'pages': pages, 'page': page, 'update': int(time.time()), 'url': req['url']}
            #  db2.update_one(
                #  {'category_id': category_id},
                #  {'$set': new},
                #  upsert=True,
            #  )
            #  time.sleep(0.75)
        #  else:
            #  new = {
                #  'category': req['category'],
                #  'sub_category': req['sub_category'],
                #  'category': req['category'],
                #  'sub_category': req['sub_category'],
                #  'pages': pages, 'page': [1, ], 'update': int(time.time()), 'url': req['url']}
            #  # pdb.set_trace()
            #  db2.update_one(
                #  {'category_id': category_id},
                #  {'$set': new},
                #  upsert=True,
            #  )
