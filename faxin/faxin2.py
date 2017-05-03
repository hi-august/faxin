# coding=utf-8

from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pdb
import requests
import json
from utils import FaxinRobot, md5
import re
from settings import MONGODB_URL
import pymongo
import time
from instance import faxin_req_info as req_info
from instance import headers

db = pymongo.MongoClient(MONGODB_URL).faxin.faxin
db_new = pymongo.MongoClient(MONGODB_URL).faxin.faxin_new
db2 = pymongo.MongoClient(MONGODB_URL).faxin.faxin_param
court  = pymongo.MongoClient(MONGODB_URL).faxin.court
db_local = pymongo.MongoClient().faxin.faxin_new
court_local  = pymongo.MongoClient().faxin.court
#  def get_test_data():
    #  for x in db_new.find({'category': u'案例'})[1:300]:
        #  db_local.save(x)
    #  for x in court.find()[1:300]:
        #  court_local.save(x)
#  get_test_data()
#  pdb.set_trace()
# for x in db_new.find({'category': u'案例'}).batch_size(30):
    # print(x)
    # pdb.set_trace()
    # x.pop('_id', None)
    # x.pop('link_id', None)
    # gid = re.search(r'gid=\S+&', x['url'])
    # if gid:
        # x['gid'] = gid.group(0)[4:-1]
    # db_new.update_one({'gid': x['gid']}, {'$set': x}, upsert=True)

def get_list(req, n=1):
    ss = requests.session()
    data = json.loads(req['param'])
    for x, y in data.items():
        if 'Page' in x:
            data[x] = str(n)
    print(req['url'], n)
    res = ss.post(req['url'], data=data, headers=headers, cookies=cookies)
    soup = bs(res.content.replace('\\', ''), 'html5lib')
    pages = soup.find_all('a')[-1].get('onclick', '')
    pages = int(re.findall(r'\d+', pages)[-1])
    info = soup.find_all('div', attrs={'class': 'fz-title1'})
    if len(info) <  50:
        if '登陆' in res.content:
            cks()
        get_list(req, n)
    for x in info[:50]:
        url = '/'.join(res.url.split('/')[:-1]) + '/' + x.find('a').get('href', '')
        print(url)
        gid = re.search(r'gid=\S+&', url)
        if gid:
            gid  = gid.group(0)[4:-1]
        else:
            gid = re.search(r'gid=\S+', url)
            if gid:
                gid  = gid.group(0)[4:]
        link_id = md5(url)
        new = {
            'category': req['category'],
            'sub_category': req['sub_category'],
            'url': url, 'link_id': link_id}
        db.update_one({'gid': gid}, {'$set': new}, upsert=True)
    key = req['url'] + '|' + str(req.get('libid', 0))
    category_id = md5(key)
    t = db2.find_one({'category_id': category_id})
    # pdb.set_trace()
    new = {}
    if t:
        page = t.get('page', [])
        if n not in page:
            page.append(n)
        if len(page) == t.get('pages', 1):
            new = {
            'category': req['category'],
            'sub_category': req['sub_category'],
                'finished': 1,
                # 'pages': pages,
                'page': page, 'update': int(time.time())}
        else:
            new = {
            'category': req['category'],
            'sub_category': req['sub_category'],
                # 'pages': pages,
                'page': page, 'update': int(time.time()), 'url': req['url']}
        db2.update_one(
            {'category_id': category_id},
            {'$set': new},
            upsert=True,
        )
        time.sleep(0.75)
    else:
        new = {
            'category': req['category'],
            'sub_category': req['sub_category'],
            'category': req['category'],
            'sub_category': req['sub_category'],
            # 'pages': pages,
            'page': [1, ], 'update': int(time.time()), 'url': req['url']}
        # pdb.set_trace()
        db2.update_one(
            {'category_id': category_id},
            {'$set': new},
            upsert=True,
        )
    time.sleep(0.1)

num_map = {
    1: u'一',
    2: u'二',
    3: u'三',
    4: u'四',
    5: u'五',
    6: u'六',
    7: u'七',
    8: u'八',
    9: u'九',
    10: u'十',
    11: u'十一',
    12: u'十二',
    13: u'十三',
    14: u'十四',
    15: u'十五',
    16: u'十六',
    17: u'十七',
    18: u'十八',
    19: u'十九',
    20: u'二十',
    21: u'二十一',
    22: u'二十二',
    23: u'二十三',
    24: u'二十四',
    25: u'二十五',
    26: u'二十六',
    27: u'二十七',
    28: u'二十八',
    29: u'二十九',
    30: u'三十',
    31: u'三十一',
    32: u'三十二',
    33: u'三十三',
    34: u'三十四',
    35: u'三十五',
    36: u'三十六',
    37: u'三十七',
    38: u'三十八',
    39: u'三十九',
    40: u'四十',
    41: u'四十一',
    42: u'四十二',
    43: u'四十三',
    44: u'四十四',
    45: u'四十五',
    46: u'四十六',
    47: u'四十七',
    48: u'四十八',
    49: u'四十九',
    50: u'五十',
    51: u'五十一',
    52: u'五十二',
    53: u'五十三',
    54: u'五十四',
    55: u'五十五',
    56: u'五十六',
    57: u'五十七',
    58: u'五十八',
    59: u'五十九',
    60: u'六十',
}

regexes = [re.compile(m) for m in [
    u'第\S+章','u第\S+条', u'第\S+节',
]]

def deal_with_content(tmp, default=u'章', is_key=False):
    '''获取具体章节'''
    bar_list = []
    for i, x in enumerate(tmp):
        ipdb.set_trace()
        if re.search(ur'第[一二三四五六七八九十零百千]{1,}%s'%default, x):
            k = re.search(ur'第[一二三四五六七八九十零百千]{1,}%s'%default,x).group(0)
            print k
            if default in x:
                new = {'index': i, 'name': x}
                if is_key:
                    pre_value = x.replace(k, '')
                    new  = {'index': i, 'name': k, 'value': [pre_value]}
                bar_list.append(new)
                # return new
    return bar_list

def deal_with_chapter(cha_list, tmp):
    '''取得具体值'''
    res = []
    for i, x in enumerate(cha_list):
        try:
            value = tmp[x['index']+ 1: cha_list[i+1]['index']]
        except:
            value = tmp[x['index']+ 1: ]
        if x.get('value', []):
            x.get('value', '').extend(value)
            new = {'value':  x.get('value'), 'index': x['index'], 'name': x['name']}
        else:
            new = {'value': value, 'index': x['index'], 'name': x['name']}
        res.append(new)
    return res

def get(url):
    ss = requests.session()
    print(url)
    res = ss.get(url, headers=headers, cookies=cookies)
    soup = bs(res.content, 'html5lib')
    law_title = soup.find('div', attrs={'class': 'law-title'}).text.strip()
    title_m = soup.find('div', attrs={'class': 'title_m'}).text.strip()
    info = soup.find_all('div', attrs={'class': 'naturePop'})
    info2 = soup.find('div', attrs={'class': 'fulltext'})
    # ipdb.set_trace()
    quotes = soup.find('div', attrs={'class': 'title_s'})
    tmp = []
    for y in info2.strings:
        if y.strip():
            tmp.append(y.strip())
    # for i, x in enumerate(tmp):
        # if re.search(u'第\S{1,4}章', x):
            # k = re.search(u'第\S{1,4}章',x).group(0)
            # print k
            # if u'章' in x:
                # new = {'index': i, 'name': x}
                # cha_list.append(new)

                # elif u'节' in x:
                    # new = {'index': i, 'name': x}
                    # sec_list.append(new)
                # elif u'条' in x:
                    # new = {'index': i, 'name': x}
                    # bar_list.append(new)
    content = []
    cha_list = deal_with_content(tmp)
    # 取得章的列表索引
    if cha_list and len(cha_list) > 5:
        tmp2 = {}
        cha_content = deal_with_chapter(cha_list, tmp)
        if cha_content:
            for x in cha_content:
                if not x['value']:
                    continue
                bar_list = deal_with_content(x['value'], u'条', is_key=True)
                if bar_list:
                    sub_value = deal_with_chapter(bar_list, x['value'])
                    for i, z in enumerate(sub_value):
                        sub_value[i]['value'] = ''.join(z['value']).strip()
                        sub_value[i].pop('index', None)
                        # ipdb.set_trace()
                    tmp2 = {'chapter': x['name'], 'data': sub_value}
                    content.append(tmp2)
                pass
    else:
        tmp2 = {}
        bar_list = deal_with_content(tmp, u'条', is_key=True)
        ipdb.set_trace()
        if bar_list:
            sub_value = deal_with_chapter(bar_list, tmp)
            for i, z in enumerate(sub_value):
                sub_value[i]['value'] = ''.join(z['value']).strip()
                sub_value[i].pop('index', None)
            ipdb.set_trace()
            tmp2 = {'chapter': z['name'], 'data': sub_value}
            content.append(tmp2)

    ipdb.set_trace()
    legal_history = []
    attr_tag = []
    for y in info:
        if y.find('div', attrs={'class': 'timeMod'}) and y.find('div', attrs={'class': 'time-p'}) and not y.find('div', attrs={'class': 'js_pop2'}):
            if legal_history:
                continue
            for x in y.find_all('div', attrs={'class': 'clearfix'}):
                date = x.find('div', attrs={'class': 'time-t1'}).text
                name = x.find('div', attrs={'class': 'time-t3'}).text
                tmp = {'date': date, 'name': name}
                legal_history.append(tmp)
        elif y.find('div', attrs={'class': 'nat-listMod'}):
            if attr_tag:
                continue
            for x in y.find_all('li', attrs={'class': 'clearfix'}):
                name = x.text.split()[0]
                value = x.text.split()[1]
                tmp = {'name': name,'value': value}
                attr_tag.append(tmp)
    # http://www.faxin.cn/lib/zyfl/GetCommonData.ashx?gid=A191317&top=200&left=240&tiao=0
    quote = []
    try:
        for i, y in enumerate(quotes.find_all('a', attrs={'fid': True})):
            try:
                gid = y.get('fid', '')
                name = y.text.strip()
                tmp = {'gid': gid, 'name': name}
            except:
                pass
    except:
        pass
    attrs = dict(
        law_title=law_title,
        title_m=title_m,
        content=content,
        attr_tag=attr_tag,
        legal_history=legal_history,
        quote=quote,
        url=url,
    )
    # print(attrs)
    db_local.save(attrs)
    # pdb.set_trace()


def cks():
    robot = FaxinRobot()
    cookies = robot.get_good_robot()
    while not cookies:
        robot.add_random_robot(5)
        cookies = robot.get_good_robot()
    return cookies
cookies = cks()
print(cookies)

# def get_tree(url):
    # pass

# url = 'http://www.faxin.cn/lib/zyfl/zyflcontent.aspx?gid=A233874&libid=010103'
url = 'http://www.faxin.cn/lib/dffl/dfflcontent.aspx?gid=B929466&libid=010201'
url = 'http://www.faxin.cn/lib/zyfl/ZyflContent.aspx?gid=A233244&libid=010102'
#  get(url)
# for x in db.find()[0:150]:
    # get(x['url'])

for x in req_info:
    get_list(x)

# if __name__ == '__main__':
    # unfinished = [1]
    # while unfinished:
        # cookies = cks()
        # for x in req_info:
            # try:
                # key = x['url'] + '|' + str(x.get('libid', ''))
                # category_id = md5(key)
                # t = db2.find_one({'category_id': category_id})
                # if t:
                    # page = t.get('page', [])
                    # pages = range(1, t.get('pages', 1)+1)
                    # unfinished = list(set(pages) - set(page))
                    # if unfinished:
                        # pdb.set_trace()
                        # for y in unfinished:
                            # try:
                                # get_list(x, y)
                            # except:
                                # cookies = cks()
                                # get_list(x, y)
                # else:
                    # print('%s no item' %category_id)
            # except Exception as e:
                # print(e)
