# encoding=utf-8
import random
import base64
import time
from user_agents import agents
import pdb
import json

from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware
import settings
#  from scrapy.conf import settings
from scrapy.utils.response import response_status_message
from utils import FaxinRobot
import logging

# from cookies import cookies
logger= logging.getLogger('DBMiddlewares')

Q = {}
class AbuYunProxyMiddleware(object):
    def process_request(self, request, spider):
        if settings.PROXY_URL:
            request.meta['proxy'] = settings.PROXY_URL
            encoded_user_pass = base64.encodestring(settings.PROXY_USERINFO)
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass.strip()
            # print(request.headers)

    def process_exception(self, request, exception, spider):
        sleep_time = 10
        logger.info("request:%s process_exception [] failed! exception: %s, sleep(%s) to again!", request.url, str(exception), sleep_time)
        time.sleep(sleep_time)
        return self._retry(request, exception, spider)

    def _retry(self, request, reason, spider):
        retryreq = request.copy()
        retryreq.dont_filter = True
        logger.info("request abuyun:%s retry", request.url)
        return retryreq

class DBRetryMiddleware(RetryMiddleware):
    def __init__(self, settings):
        #  if not settings.getbool('RETRY_ENABLED'):
            #  raise NotConfigured
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('DB_RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    def vcode(self):
        pass

    def process_response(self, request, response, spider):
        content_length = response.headers.get("Content-Length")
        if '"remind"' == response.body:
            reason = 'vcode retry'
            # pdb.set_trace()
            return self._retry(request, reason, spider)

        if 'login.aspx' in response.url or 'error.aspx' in response.url:
            robot = FaxinRobot()
            robot.remove_robot(request.cookies)
            cookies = robot.get_good_robot()
            while not cookies:
                robot.add_random_robot(1)
                cookies = robot.get_good_robot()

            request.cookies = cookies
            Q.update({'cookies': cookies})
            print(request.cookies)
            reason = 'cookies update'
            return self._retry(request, reason, spider)

        #  if u'您的访问频率过快' in response.body:
            #  time.sleep(1.75)
            #  return self._retry(request, reason, spider)

        if response.status == 200 and content_length:
            if len(response.body) != content_length:
                response.status = 500
                return response

        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)

            # logger.info("request [%s] failed! status: %d, reason: %s", response.url, response.status, reason)
            status = response.status
            if status == 403:
                sleep_time = 10
                logger.info("request [%s] failed! status: %d, sleep(%ds) to again!", response.url, response.status, sleep_time)
                time.sleep(sleep_time)
            elif status == 302:
                robot = FaxinRobot()
                robot.remove_robot(request.cookies)
                cookies = robot.get_good_robot()
                while not cookies:
                    robot.add_random_robot(1)
                    cookies = robot.get_good_robot()
                Q.update({'cookies': cookies})
                request.cookies = cookies
                print(request.cookies)
                reason = 'cookies update'
                sleep_time = 3
                logger.info("request [%s] failed! status: %d, sleep(%ds) to again!", response.url, response.status, sleep_time)
                time.sleep(sleep_time)
            elif status == 301:
                sleep_time = 10
                logger.info("request [%s] failed! status: %d, sleep(%ds) to again!", response.url, response.status, sleep_time)
                time.sleep(sleep_time)
            elif status == 429:
                sleep_time = 1
                logger.info("request [%s] failed! status: %d, sleep(%ds) to again!", response.url, response.status, sleep_time)
                time.sleep(sleep_time)
            elif status == 503:
                sleep_time = 10
                logger.info("request [%s] failed! status: %d, sleep(%ds) to again!", response.url, response.status, sleep_time)
                time.sleep(sleep_time)
            else:
                pass
            return self._retry(request, reason, spider) or response
        return response

class UserAgentMiddleware(object):
    """ 换User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent


class CookiesMiddleware(object):
    def __init__(self):
        robot = FaxinRobot()
        #  pdb.set_trace()
        self.cookies = robot.get_good_robot()
        while not self.cookies:
            robot.add_random_robot(5)
            self.cookies = robot.get_good_robot()
        Q.update({'cookies': self.cookies})


    def process_request(self, request, spider):
        request.cookies = Q.get('cookies', {})
