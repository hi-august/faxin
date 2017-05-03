# coding=utf-8

import redis
import settings
import requests
from bs4 import BeautifulSoup as bs
import json
import pdb
import hashlib
from random import choice
from instance import faxin_user_info as users
from instance import headers
from screct import PROXY_USERINFO
from random import Random
#  import os
#  import sys
#  path = os.path.abspath(os.getcwd())
#  print(path)
#  sys.path.append(path)

proxies = {
    'http': 'http://%s@proxy.abuyun.com:9020'%PROXY_USERINFO,
    'https': 'http://%s@proxy.abuyun.com:9020'%PROXY_USERINFO,

}

def md5(msg):
    md5 = hashlib.md5(msg.encode('utf-8')).hexdigest()
    return md5

def random_str(randomlength=6):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str+=chars[random.randint(0, length)]
    return str

def ecp(im, dcount=6):
    frame = im.load()
    (w, h) = im.size
    for i in xrange(w):
        for j in xrange(h):
            if frame[i, j] != 255:
                count = 0
                try:
                    if frame[i, j - 1] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i, j + 1] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i - 1, j - 1] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i - 1, j] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i - 1, j + 1] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i + 1, j - 1] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i + 1, j] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i + 1, j + 1] == 255:
                        count += 1
                except IndexError:
                    pass
                if count >= dcount:
                    frame[i, j] = 255
    return im

_redis_pool_list = {}
def get_redis(name):
    if name not in _redis_pool_list:
        if not settings.REDIS_PASS:
            pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                socket_timeout=10,
                db=0,
            )
        else:
            pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASS,
                socket_timeout=10,
                db=0,
            )

        _redis_pool_list[name] = pool
    return redis.Redis(connection_pool=_redis_pool_list[name])

class RobotConsumer(object):
    name = 'base'

    def valid_robot(self, cookies):
        return True

    def get_robot(self):
        rds = get_redis("default")
        cookies = rds.srandmember(self.name)
        return cookies

    def on_producer_add(self, cookies):
        if self.valid_robot(cookies):
            self.add_robot(cookies)

    def on_producer_remove(self, cookies):
        self.remove_robot(cookies)

    def add_robot(self, cookies):
        rds = get_redis("default")
        add_cnt = rds.sadd(self.name, cookies)
        return add_cnt


    def remove_robot(self, cookies):
        rds = get_redis("default")
        del_cnt = rds.srem(self.name, cookies)
        return del_cnt

    def all_robot(self):
        rds = get_redis("default")
        return rds.smembers(self.name)

    def robot_size(self):
        rds = get_redis("default")
        return rds.scard(self.name)

class FaxinRobot(RobotConsumer):
    name = 'faxin:cookies'

    def valid_robot(self, cookies):
        try:
            url = 'http://www.faxin.cn/index.aspx'
            res = requests.get(url,
                               headers=headers,
                               cookies=json.loads(cookies),
                               proxies=proxies,
                               )
            u = bs(res.content, 'html5lib').find('span', attrs={'class': 'user'}).text
            if u:
                print('Cookies Success valid_robot ==> %s'%u)
                return True
            else:
                print('Cookies is Failed!!!')
                return False
        except Exception as e:
            print(e)
            return False

    def get_good_robot(cls, retry=0):
        cookies = cls.get_robot()
        if not cookies:
            cls.add_random_robot(1)
        if cls.valid_robot(cookies):
            try:
                return json.loads(cookies)
            except Exception as e:
                print(e, cookies)
                return cookies
        else:
            cls.remove_robot(cookies)
            retry += 1
            if retry > 2:
                return None
            return cls.get_good_robot(retry=retry)

    def add_cookies(self, user):
        url = 'http://www.faxin.cn/login.aspx'
        y = user.split('|')
        ss = requests.Session()
        # retry = 0
        # try:
            # rr = ss.get(url, headers=headers, proxies=proxies)
        # except:
            # retry+=1
            # if retry > 2:
                # return None
            # return self.add_cookies(user)
        # state = bs(rr.content, 'html5lib').find('input', attrs={'id': '__VIEWSTATE'}).get('value', '')
        # print(state)
        state = '/wEPDwUKMTY1MjQzNTY1MGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgIFCmlzUmVtZW1iZXIFC2lzQXV0b0xvZ2lu'
        postData = {
            '__VIEWSTATE': state,
            'user_name': y[0],
            'user_password': y[1],
            'isRemember': 'on',
            'isAutoLogin': 'on',
        }
        retry = 0
        try:
            rr = ss.post(url, data=postData)
        except:
            retry += 1
            if retry > 2:
                return None
            return self.add_cookies(user)
        if rr.url == "http://www.faxin.cn/index.aspx":
            print("Get Cookie Success!( Account:%s )" % user)
            cookie = ss.cookies.get_dict()
            cks = json.dumps(cookie)
            return cks
        else:
            reason = bs(rr.content, 'html5lib').find_all('script')[-1].text
            print("Failed!( Reason:%s )" % reason)
            return ''

    def add_random_robot(cls, default=30):
        try:
            redis_faxin_users = [json.loads(y)['username'] for y in cls.all_robot()]
        except:
            redis_faxin_users = []
        for x in xrange(default):
            user = choice(users)
            if user not in redis_faxin_users:
                print('add_random_robot %s' %(user))
                cookies = cls.add_cookies(user)
                cls.add_robot(cookies)
                if cookies and default==1:
                    return cookies
