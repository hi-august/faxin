# encoding=utf-8
import json
import requests
from register_faxin import headers
from bs4 import BeautifulSoup as bs
# from utils import RobotConsumer
from register_faxin import user
import pdb
import random


# user = [
    # '13000201599|5c1dT2GZ',
    # 'cxk517|cxk517',
# ]

# robot = RobotConsumer()

def add_cookies(user):
    #  cookies = []
    # loginURL = r'http://www.faxin.cn/login.aspx'
    url = 'http://www.faxin.cn/login.aspx'
    for x in user:
        y = x.split('|')
        ss = requests.Session()
        rr = ss.get(url, headers=headers)
        state = bs(rr.content, 'lxml').find('input', attrs={'id': '__VIEWSTATE'}).get('value', '')
        postData = {
            '__VIEWSTATE': state,
            'user_name': y[0],
            'user_password': y[1],
            'isRemember': 'on',
            'isAutoLogin': 'on',
        }
        rr = ss.post(url, data=postData)
        if rr.url == "http://www.faxin.cn/index.aspx":
            print "Get Cookie Success!( Account:%s )" % x
            cookie = ss.cookies.get_dict()
            cks = json.dumps(cookie)
            # pdb.set_trace()
            # robot.add_robot(cks)
            return cks
            #  cookies.append(cookie)
        else:
            return ''
            reason = bs(rr.content, 'lxml').find_all('script')[-1].text
            print "Failed!( Reason:%s )" % reason

#  def check_cookies(cookies=''):
    #  url = 'http://www.faxin.cn/index.aspx'
    #  # if cookies:
        #  # pass
    #  for x in robot.all_robot():
        #  try:
            #  res = requests.get(url, headers=headers, cookies=json.loads(x))
            #  u = bs(res.content, 'lxml').find('span', attrs={'class': 'user'}).text
            #  if u:
                #  print('Cookies Success Checked ==> %s'%u)
                #  pass
            #  else:
                #  print('Cookies is Failed!!!')
                #  robot.remove_robot(x)
        #  except Exception as e:
            #  print(e)

# cookies = add_cookies([random.choice(user), ])
# cookie = ''
# check_cookies()

if __name__ == '__main__':
    pass
#  cookies = getCookies(user)
#  print "Get Cookies Finish!( Num:%d)" % len(cookies)
