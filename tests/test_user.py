# coding: utf-8

from nose.tools import with_setup

import leancloud
from leancloud import User
from leancloud import Query

__author__ = 'asaka <lan@leancloud.rocks>'

# user = None


def setup_func():
    leancloud.init(
        'pgk9e8orv8l9coak1rjht1avt2f4o9kptb0au0by5vbk9upb',
        master_key='azkuvukzlq3t38abdrgrwqqdcx9me6178ctulhd14wynfq1n',
    )
    users = Query(User).find()
    for u in users:
        u.destroy()

    # global user
    # user = User(username='example', password='example')
    user = User()
    user.set('username', 'example')
    user.set('password', 'example')
    user.sign_up()


def destroy_func():
    pass


@with_setup(setup_func, destroy_func)
def test_sign_up():
    user = User()
    user.set('username', 'foo')
    user.set('password', 'bar')
    user.sign_up()
    assert user._session_token


@with_setup(setup_func, destroy_func)
def test_login():
    user = User()
    user.set('username', 'example')
    user.set('password', 'example')
    user.login()
