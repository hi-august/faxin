# coding=utf-8

from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pdb
import requests
import json
from settings import MONGODB_URL
import pymongo
import time
import re
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# import ipdb

db = pymongo.MongoClient(MONGODB_URL).faxin.court_category
db2 = pymongo.MongoClient(MONGODB_URL).faxin.court_param
db_local = pymongo.MongoClient().faxin.court
db3 = pymongo.MongoClient().faxin.court_category


# li = [u'金融借款合同纠纷', u'同业拆借纠纷', u'企业借贷纠纷', u'民间借贷纠纷', u'小额借款合同纠纷', u'金融不良债权追偿纠纷']
info = db3.find_one({u'文书类型': {'$exists': True}})
info2 = db.find_one({u'文书类型': {'$exists': True}})
#  pdb.set_trace()
# query = {'pages': {'$gt': 100}, 'new6': 1}
# more = db2.find(query)
# for x in more:
    # for y in li:
        # param = x.get('param', '')
        # if param:
            # p = u'%s,%s:%s' %(param, u'五级案由', y)
            # data = {'new7': 1, 'param': p}
            # print p
            # db2.update_one({'param': p}, {'$set': data}, upsert=True)
def get_date():
    dates = []
    now = datetime.datetime.now()
    default_date = datetime.datetime(2013, 7, 1, 0, 0)
    query_date = datetime.timedelta(days=1) + default_date
    while query_date < now:
        start = query_date.strftime('%Y-%m-%d')
        query_date += datetime.timedelta(days=1)
        end = query_date.strftime('%Y-%m-%d')
        param = u'上传日期:%s TO %s,'%(start, end)
        dates.append(param)
    return dates

# def gen_new_param():
    # dates = get_date()
    # for x in dates:
        # if x:
            # p = u'%s案件类型:民事案件,文书类型:判决书'%(x)
            # print p
            # data = {'new200': 1, 'param': p.strip()}
            # db2.update_one({'param': p}, {'$set': data}, upsert=True)
# gen_new_param()

def gen_new_param():
    courts = []
    #  query = {'pages': {'$gt': 100}, 'new3': 1}
    info = db2.find({'new206': 1, 'pages': {'$gt': 100}})
    print(info.count())
    info2 = db.find({u'三级案由': {'$exists': True}})
    for x in info2:
        for y in x[u'三级案由']:
            # pdb.set_trace()
            courts.append((y, x['root']))
    courts = list(set(courts))
    for x in info:
        for y in courts:
            if x and y:
                param = x['param']
                if ':,' in param:
                    continue
                #  pdb.set_trace()
                if y[1] not in param:
                    continue
                p = u'%s,%s:%s' %(param, u'三级案由', y[0])
                print p
                data = {'new207': 1, 'param': p.strip()}
                db2.update_one({'param': p}, {'$set': data}, upsert=True)
#  gen_new_param()
#  info2 = db.find({u'四级案由': {'$exists': True}})
#  for x in info:
    #  print(x['param'])
#  li = []
#  for x in info2:
    #  li.extend(x[u'四级案由'])
#  li = list(set(li))
#  print(len(li))
#  for y in li:
    #  if y:
        #  p = u'案件类型:民事案件,文书类型:判决书,%s:%s'%(u'四级案由', y)
        #  #  print p
        #  data = {'new30': 1, 'param': p}
        #  print(data['param'])
        #  db2.update_one({'param': p}, {'$set': data}, upsert=True)
        #  param = x['param']
        #  p = u'%s,%s:%s' %(param, u'关键词', y)
        #  data = {'new61': 1, 'param': p}
        #  print p
        #  db2.update_one({'param': p}, {'$set': data}, upsert=True)
#  info2 = db.find_one({u'文书类型': {'$exists': True}})
#  for x in info:
    #  for y in x[u'基层法院']:
        #  print y
        #  tmp = {'root': x.get('root', ''), u'基层法院': y}
        #  if tmp not in courts:
            #  courts.append(tmp)
#  print info[u'法院地域']
#  for x in info[u'法院地域']:
    #  courts.append(x)
#  courts = list(set(courts))
#  print(len(courts))
#  for y in courts:
    #  p = u'案件类型:民事案件,文书类型:判决书,%s:%s'%(u'法院地域', y)
    #  print p
    #  data = {'new60': 1, 'param': p}
    #  db2.update_one({'param': p}, {'$set': data}, upsert=True)
# query = {'pages': {'$gt': 100}, 'new3': 1}
# more = db2.find(query).count()
# print more, db2.find(query)[1]
# for x in more:
    # print x.get('param')
# print more, len(courts)
# print more, info
# n = 0
# for y in more:
    # for x in courts:
        # tmp = y.get('param')
        # # print tmp
        # if x['root'] in tmp:
            # p = tmp + u',%s:%s' %(u'基层法院', x[u'基层法院'])
            # data = {'new3': 1, 'param': p}
            # print p
            # db2.update_one({'param': p}, {'$set': data}, upsert=True)

# for x in db2.find({'page': {'$exists': True}}, no_cursor_timeout=True):
    # page = x['page']
    # n = [int(y) for y in page]
    # new = {'page': n}
    # print(x['param'])
    # db2.update_one({'param': x['param']}, {'$set': new})
    # if len(set(x['page'])) != int(x['pages']):
        # if (len(set(x['page'])) != 1) and (int(x['pages']) != 0):
            # try:
                # pages = x['pages']
                # pages = [unicode(y) for y in range(1, pages+1)]
                # print(
                    # x,
                    # set(pages) - set(x['page'])
                # )
                # # new = {'page': list(set(x['page']))}
                # db2.update_one({'param': x['param']}, {'$unset': {'finished': 1}})
            # except Exception as e:
                # print(e)
        # print x

# info = db.find_one({u'文书类型': {'$exists': True}})
# #  print info
# four = db.find({u'四级案由': {'$exists': True}}, no_cursor_timeout=True)
# basic = db.find({u'基层法院': {'$exists': True}}, no_cursor_timeout=True)

# fours = set()
# basics = set()
# for b in four:
    # for c in b[u'四级案由']:
        # if c:
            # fours.add(c)

# for b in basic:
    # for c in b[u'基层法院']:
        # if c:
            # basics.add(c)

# #  tmp = set()
# for x in info[u'关键词']:
    # for b in fours:
        # for c in basics:
            # if (not x) and (not b) and (not c):
                # continue
            # param = u'文书类型:判决书,%s:%s,%s:%s,%s:%s'%(u'关键词', x, u'四级案由', b, u'基层法院', c)
            # #  print(param)
            # db.save({'param': param})
            # time.sleep(0.1)
            #  tmp.add(param)
#  param = '文书类型:判决书'
#  params = {'param': list(tmp)}
#  db.save(params)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
    'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': "*/*",
}

data = {
    'Direction': 'asc',
    'Index': '100',
    'Order': u'法院层级',
    'Page': '20',
    'Param': u'文书类型:判决书,关键词:合同',
}

def get_list(url):
    res = requests.post(url, headers=headers, data=data)
    res = deal_with_content(res.content)
    info = res[1:]
    total = res[0]['Count']
    for x in info:
        attrs = dict(
        case_name = x.get(u'案件名称', ''),
        pub_date = x.get(u'裁判日期', ''),
        case_raw = x.get(u'裁判要旨段原文', ''),
        case_id = x.get(u'案号', ''),
        doc_id = x.get(u'文书ID', ''),
        court_proceeding= x.get(u'审判程序', ''),
        court_name= x.get(u'法院名称', ''),
        reason = x.get(u'不公开理由', ''),
        case_type = x.get(u'案件类型', ''),
        )
        print(len(attrs), len(x))
        pdb.set_trace()

    pdb.set_trace()

def deal_with_content(content):
    res = content.replace('\\', '').strip('\"')
    res = json.loads(res)
    return res

def get(url):
    res = requests.get(url)
    start = res.content.find('{\\')
    end = res.content.find('var jsonData') - 7
    soup = res.content[start: end]
    soup = deal_with_content(soup)
    Html = soup['Html']
    PubDate = soup['PubDate']
    Title = soup['Title']
    info = bs(Html, 'lxml')
    content = []
    check = {}
    clean_data = {}
    for p in info.find_all('div'):
        tmp = '\n'.join(p.strings)
        content.append(tmp)
        for regex in regexes:
            if regex.search(tmp):
                k = regex.search(tmp).group(0)
                i = content.index(tmp)
                if k in check:
                    check[k].append(i)
                else:
                    check[k] = [i, ]
                # print name_map[k], k, i
    sub_case_name = '\n'.join(content[0:2])
    for x, y in check.items():
        c = min(y)
        pdb.set_trace()
        clean_data[name_map[x]] = c
        print clean_data

    # attrs = dict(
        # PubDate=PubDate,
        # Title=Title,
        # Html=Html,
    # )
    # print(attrs)
    pdb.set_trace()

def get_tree(url, reason, n, n1):
    data = {
        #  'Direction': 'asc',
        #  'Index': '1',
        #  'Order': u'法院层级',
        #  'Page': '20',
        # 'Param': u'文书类型:判决书,关键词:合同,审判程序:一审,裁判年份:2014,法院层级:高级法院,四级案由:租赁合同纠纷,基层法院:金塔县人民法院',
        #  'Param': u'文书类型:判决书,文书类型:判决书,%s:%s'%(reason, n),
        'Param': u'案件类型:%s,%s:%s'%(reason,n1,n),
        'parval': '%s'%n,
    }
    res = requests.post(url, data=data, headers=headers)
    #  pdb.set_trace()
    res = deal_with_content(res.content)
    d = {'root': n1, 'type': reason, 'reason': n}
    for x in res:
        info = x['Child']
        tmp = []
        for y in info:
            k  = y['Field']
            v  = y['Key']
            print x['Value']
            # try:
                # info2 = x['Child']
                # for z in info2:
                    # k1 = z['Field']
                    # v1 = z['Key']
                    # if v1 not in tmp:
                        # tmp.append(v)
                    # print('new %s ==> %s'%(k1, v1))
                    # if z['Value'] == u'此节点加载中...':
                        # pass

            # except Exception as e:
                # print(e)
            if v not in tmp and v:
                tmp.append(v)
            d[k] = tmp
            tmp2 = k  + ':' + v
            print(tmp2)
    # print(d)
    #  t = db.find_one({u'\u57fa\u5c42\u6cd5\u9662': d[u'\u57fa\u5c42\u6cd5\u9662']})
    #  if t:
        #  db.update(
            #  {'_id': t['_id']},
            #  {'$set': d}
        #  )
    #  else:
        #  pdb.set_trace()

    #  pdb.set_trace()
    if len(d) > 4:
        db.save(d)


url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=bba75203-22fe-4649-be2f-e3c37e3fa978'
# get(url)
#  url = 'http://wenshu.court.gov.cn/List/ListContent'
# get_list(url)
url = 'http://wenshu.court.gov.cn/List/TreeContent'
#  url = 'http://wenshu.court.gov.cn/List/CourtTreeContent'
url = 'http://wenshu.court.gov.cn/List/ReasonTreeContent'
for x in [u'刑事案件', u'行政案件', u'赔偿案件', u'执行案件']:
    reason = u'三级案由'
    t = db.find_one({'type': x, 'root': u'二级案由'})
    if t:
        reasons = t.get(reason, [])
        for y in reasons:
            if y:
                get_tree(url, x, y, reason)

#  info2 = db.find({u'四级案由': {'$exists': True}})
#  for x in info2:
    #  #  if x:
        #  #  get_tree(url, u'三级案由', x)
    #  info = x[u'四级案由']
    #  for y in info:
        #  try:
            #  if y:
                #  get_tree(url, u'四级案由', y)
        #  except Exception as e:
            #  print(e)
