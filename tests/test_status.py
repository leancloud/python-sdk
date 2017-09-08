# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import time

from nose.tools import assert_equal
from nose.tools import assert_true

import leancloud
from leancloud import Status


def setup():
    leancloud.init(os.environ['APP_ID'], app_key=os.environ['APP_KEY'], master_key=os.environ['MASTER_KEY'])
    leancloud.use_master_key(True)
    users = leancloud.Query(leancloud.User).find()
    for u in users:
        u.destroy()
    leancloud.use_master_key(False)

    user1 = leancloud.User()
    user1.set('username', 'user1_name')
    user1.set('password', 'password')
    user1.set_email('wow@leancloud.rocks')
    user1.set_mobile_phone_number('18611111111')
    user1.sign_up()


def test_send():
    status = Status(image='http://www.example.com', message='hello world!')
    status.inbox_type = 'privateMessage'
    query = leancloud.Query('User').equal_to('username', 'user1_name')
    status.send(query)
    assert status.id
    assert status.created_at
    status.destroy()


def test_send_to_followers():
    status = Status(image='http://www.example.com', message='hello world!')
    status.send_to_followers()
    assert status.id
    assert status.created_at
    status.destroy()


def test_send_private_status():
    status = Status(image='http://www.example.com', message='hello world!')
    target = leancloud.User.create_without_data('foo')
    status.send_private_status(target)
    assert status.id
    assert status.created_at
    assert_equal(status.inbox_type, 'private')
    status.destroy()


def test_count_():
    status = Status(image='http://www.example.com', message='hello world!')
    status.send_private_status(leancloud.User.get_current())
    result = Status.count_unread_statuses(leancloud.User.get_current(), 'private')
    assert_equal(result.total, 1)
    assert_equal(result.unread, 1)
    status.destroy()
