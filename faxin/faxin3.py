# coding=utf-8

from selenium import webdriver
from bs4 import BeautifulSoup as bs
import ipdb
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
from tornado import ioloop, gen, queues
import sys

db = pymongo.MongoClient(MONGODB_URL).faxin.faxin
db_local = pymongo.MongoClient().faxin.faxin
db_new = pymongo.MongoClient(MONGODB_URL).faxin.faxin_new
db2 = pymongo.MongoClient(MONGODB_URL).faxin.faxin_param
# ipdb.set_trace()
# for x in db_new.find({'category': u'案例'}).batch_size(30):
    # print(x)
    # pdb.set_trace()
    # x.pop('_id', None)
    # x.pop('link_id', None)
    # gid = re.search(r'gid=\S+&', x['url'])
    # if gid:
        # x['gid'] = gid.group(0)[4:-1]
    # db_new.update_one({'gid': x['gid']}, {'$set': x}, upsert=True)
q = {}
def get_gid(url):
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


def get_list(req, cookies, n=1):
    print('start get_list')
    ss = requests.session()
    data = json.loads(req['param'])
    for x, y in data.items():
        if 'Page' in x:
            data[x] = str(n)
    print(req['url'], n)
    res = ss.post(req['url'], data=data, headers=headers, cookies=cookies)
    soup = bs(res.content.replace('\\', ''), 'lxml')
    pages = soup.find_all('a')[-1].get('onclick', '')
    pages = int(re.findall(r'\d+', pages)[-1])
    info = soup.find_all('div', attrs={'class': 'fz-title1'})
    # pdb.set_trace()
    if len(info) <  50:
        if '登陆' in res.content:
            cookies = cks()
        # get_list(req, n)
    if len(info) == 0:
        print('not item')
        cookies = cks()
        if cookies:
            q.update({'cookies': cookies})
        get_list(req, q['cookies'], n)
        #  ipdb.set_trace()
        #  sys.exit()
    for x in info[:50]:
        url = '/'.join(res.url.split('/')[:-1]) + '/' + x.find('a').get('href', '')
        print(url)
        gid = get_gid(url)
        # link_id = md5(url)
        new = {
            'category': req['category'],
            'sub_category': req['sub_category'],
            'url': url,
            # 'link_id': link_id
        }
        try:
            db_new.update_one({'gid': gid}, {'$set': new}, upsert=True)
        except Exception as e:
            pdb.set_trace()
            print e
    try:
        url
    except:
        print('restart')
        sys.exit()
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

def get(url):
    ss = requests.session()
    print(url)
    gid = get_gid(url)
    res = ss.get(url, headers=headers, cookies=cookies)
    soup = bs(res.content, 'lxml')
    law_title = soup.find('div', attrs={'class': 'law-title'})
    title_m = soup.find('div', attrs={'class': 'title_m'}).text.strip()
    quotes = soup.find('div', attrs={'class', 'title_s'})
    content = soup.find('div', attrs={'class': 'fulltext'})
    if quotes:
        content.div.decompose()
    if title_m:
        title_m = title_m.text.strip()
        content.div.decompose()
    ipdb.set_trace()
    content = '|||'.join(content.strings)
    content = '|||'.join(content.split())
    content = re.sub(r'[\|]{3,}','|||', content)
    legal_history = []
    attr_tag = []
    info = soup.find_all('div', attrs={'class': 'naturePop'})
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
    print(attrs)
    pdb.set_trace()


def cks():
    robot = FaxinRobot()
    cookies = robot.get_good_robot()
    while not cookies:
        robot.add_random_robot(1)
        cookies = robot.get_good_robot()
    return cookies
# print(cookies)

# def get_tree(url):
    # pass

# url = 'http://www.faxin.cn/lib/zyfl/zyflcontent.aspx?gid=A233874&libid=010103'
# get(url)
# for x in db.find()[:20]:
    # get(x['url'])

# for x in req_info:
    # get_list(x)
def start():
    cookies = cks()
    if cookies:
        q.update({'cookies': cookies})
    unfinished = [1]
    while unfinished:
        for x in req_info:
            try:
                key = x['url'] + '|' + str(x.get('libid', ''))
                category_id = md5(key)
                t = db2.find_one({'category_id': category_id})
                if t:
                    page = t.get('page', [])
                    pages = range(1, t.get('pages', 1)+1)
                    # unfinished.remove(1)
                    unfinished = list(set(pages) - set(page))
                    if unfinished:
                        for y in unfinished:
                            try:
                                get_list(x, q['cookies'], y)
                            except:
                                sys.exit()
                                #  cookies = cks()
                                #  get_list(x, y)
                else:
                    print('%s no item' %category_id)
            except Exception as e:
                print(e)
                sys.exit()

if __name__ == '__main__':
    start()
