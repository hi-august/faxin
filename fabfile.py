#!/usr/bin/env python
# encoding: utf-8

from fabric.api import env
from fabric.operations import run
from fabric.context_managers import cd

SERVER_LIST = {
    # "master": "114.215.148.175",
    "slave": "47.92.82.132",
    "slave2": '47.93.124.25',
    "slave3": '47.93.124.65',
}

env.user = 'root'
env.hosts = SERVER_LIST.values()


def deploy(name=""):
    if name not in ("court", ):
        raise Exception("name should be in (court), but it's %s" % name)

    with cd("/opt/faxin/"):
        # 拉代码
        run('git checkout .')
        run("git checkout master")
        run("git fetch")
        run("git merge origin/master")
        pass

        # 重启supervisor
        #  run("sudo supervisorctl restart server:%s" % name)


def deploy_all():
    with cd("/opt/faxin/"):
        # 拉代码
        run('git checkout .')
        run("git checkout master")
        run("git fetch")
        run("git merge origin/master")

        # for name in ["court", ]:
            # 重启supervisor
        run("sudo supervisorctl restart all")
