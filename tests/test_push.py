# coding: utf-8

from nose.tools import with_setup

import leancloud
from leancloud import push

__author__ = 'asaka'


def setup_func():
    leancloud.init(
        'pgk9e8orv8l9coak1rjht1avt2f4o9kptb0au0by5vbk9upb',
        'hi4jsm62kok2qz2w2qphzryo564rzsrucl2czb0hn6ogwwnd',
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
