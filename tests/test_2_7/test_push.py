# coding: utf-8

from nose.tools import with_setup

import leancloud
from leancloud import push

__author__ = 'asaka'


def setup_func():
    leancloud.init(
        '6mnpbdqufkybpfwev1jww7ynrqtzv38vadgzlx37rinn9fwk',
        'ur7kqm0qyukk2lgzzi5iqd3pym53dfdj8h3t2fksbkbdptt8',
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
