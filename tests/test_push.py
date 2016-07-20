# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from datetime import datetime

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
    instanlation = leancloud.Installation()
    instanlation.set('deviceType', 'ios')
    instanlation.set('deviceToken', 'xxx')
    instanlation.save()

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
    t = datetime.fromtimestamp(0)
    query = leancloud.Query('_Installation').equal_to('objectId', 'xxx')
    notification = push.send(data, where=query, push_time=datetime.now())
    assert(notification.id)
