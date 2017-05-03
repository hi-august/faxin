# coding=utf-8

import requests
import pdb
from bs4 import BeautifulSoup as bs
from PIL import Image
from pytesseract import image_to_string
import time
from instance import faxin_user_info as user
from instance import headers
from utils import ecp
import requests
from bs4 import BeautifulSoup as bs
from utils import random_str
import ipdb


def get_phone(url):
    phone = []
    for x in xrange(15, 30):
        res = requests.get(url%x)
        soup = bs(res.content, 'lxml')
        li = [x.text.strip()+'|'+random_str() for x in soup.find('div', attrs={'class': 'ListLink2'}).find_all('li')]
        phone.extend(li)
        time.sleep(1.25)
    ipdb.set_trace()

url = 'http://www.hiphop8.com/more.php?page=%s'
#  get_phone(url)


vcode_url = 'http://www.faxin.cn/Regist/ValidateCode.aspx'

def register(url, u, pwd):
    rr = requests.get(vcode_url, headers)
    with open('faxin.png', 'wb') as f:
        f.writelines(rr.content)
    # 打开os error
    im = Image.open('faxin.png')
    im = im.convert('L')
    im = im.point(lambda x: 255 if x > 120 else 0)
    im = ecp(im, 8)
    vcode = image_to_string(im, lang='faxin', config='-psm 8')
    #  vcode = str(raw_input('enter faxin code: '))
    r_url = 'http://www.faxin.cn/Regist/Regist.aspx'
    rr = requests.get(r_url, headers=headers, cookies=rr.cookies)
    state = bs(rr.content, 'lxml').find('input', attrs={'id': '__VIEWSTATE'}).get('value', '')
    data = {
        '__VIEWSTATE': state,
        'email': u + '@163.com',
        'username': u,
        'userpwd': pwd,
        'chkuserpwd': pwd,
        'contact': '',
        'contact_tel: u,'
        'chkmail|on': '',
        'hiddRecMail': '1',
        'texcode': vcode,
        'Button1': '注册',

    }
    print(data, rr.cookies)
    rr = requests.post(url, data=data, cookies=rr.cookies, headers=headers)
    if '注册成功' in rr.content:
        print(u'%s : %s ==> 注册成功' %(u, pwd))
    else:
        tmp = u + '|' + pwd
        failed.add(tmp)
    time.sleep(3)
    print(rr)

url = 'http://www.faxin.cn/Regist/Regist.aspx'
if __name__ == '__main__':
    failed = set(user[:-400])
    while len(failed):
        x = failed.pop()
        y = x.split('|')
        register(url, y[0], y[1])
    #  for x,y in user.items()[1:]:
        #  register(url, x, y)
