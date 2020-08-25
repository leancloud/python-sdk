# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import time
from datetime import datetime, timedelta

from nose.tools import with_setup  # type: ignore

import leancloud
from leancloud import push

__author__ = "asaka"


def setup_func():
    leancloud.init(os.environ["APP_ID"], os.environ["APP_KEY"])


@with_setup(setup_func)
def test_basic_push():  # type: () -> None
    installation = leancloud.Installation()
    installation.set("deviceType", "ios")
    installation.set("deviceToken", "xxx")
    installation.save()

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
    query = leancloud.Query("_Installation").equal_to("deviceToken", "xxx")
    now = datetime.now()
    two_hours_later = now + timedelta(hours=2)
    try:
        notification = push.send(
            data,
            where=query,
            push_time=now,
            expiration_time=two_hours_later,
            prod="dev",
            flow_control=0,
        )
    except leancloud.LeanCloudError as e:
        # LeanCloudError: [1] The iOS certificate file is expired or disabled.
        assert e.code == 1
    else:
        # flow_control = 0 <=> flow_control = 1000 by rest api design
        time.sleep(5)  # notification write may have delay
        notification.fetch()
        assert notification.id
        # Test that notification is read only.
        try:
            notification.save()
        except leancloud.LeanCloudError as e:
            assert e.code == 1
        else:
            raise Exception()
