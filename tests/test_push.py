# coding: utf-8

import os

from nose.tools import with_setup

import leancloud
from leancloud import push

__author__ = 'asaka'


def setup_func():
    leancloud.init(
        os.environ['appid'],
        os.environ['appkey']
    )


@with_setup(setup_func)
def test_basic_push():
    data = {
        "alert": {
            "title": "标题",
            "title-loc-key": "",
            "body": "消息内容",
            "action-loc-key": "",
            "loc-key": "",
            "loc-args": [""],
            "launch-image": "",
        }
    }
    notification = push.send(data)
    notification.fetch()
    print notification.attributes
