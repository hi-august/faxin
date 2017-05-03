#!/usr/bin/env python
# coding=utf-8

import requests
import traceback
import time
import os

from apscheduler.scheduler import Scheduler
from datetime import datetime as dte


def check(run_in_local=False):
    def wrap(func):
        def sub_wrap(*args, **kwargs):
            res = None
            try:
                # if not run_in_local:
                #     proxy_log.info("[ignore] forbid run at debug mode")
                #     return None
                t1 = time.time()
                print("[start] %s %s %s", func.__name__, args, kwargs)
                # with app.app_context():
                res = func(*args, **kwargs)
                cost = time.time() - t1
                # cron_log.info("[succss] %s %s %s, return: %s, cost time: %s", func.__name__, args, kwargs, res, cost)
                if res:
                    print("[succss] %s %s %s, return: %s, cost time: %s", func.__name__, args, kwargs, res, cost)
                else:
                    print("[succss] %s %s %s, return: , cost time: %s", func.__name__, args, kwargs, cost)
            except:
                print("%s,%s,%s", traceback.format_exc(), args, kwargs)
            return res
        return sub_wrap
    return wrap

@check(run_in_local=False)
def start_get_faxin_list():
    from faxin3 import start
    print(start_get_faxin_list.__name__)
    start()

def main():
    sched = Scheduler(daemonic=False)
    sched.add_interval_job(start_get_faxin_list, minutes=5)
    sched.start()

if __name__ == '__main__':
    print('start cron job ...')
    main()
