# coding: utf-8

import os

from nose.tools import with_setup

import leancloud
from leancloud import push

__author__ = 'asaka'


def setup_func():
    leancloud.init(
        os.environ['APP_ID'],
        os.environ['APP_KEY']
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
    query = leancloud.Query('_Installation').equal_to('objectId', 'xxx')
    notification = push.send(data, where=query)
    notification.fetch()
