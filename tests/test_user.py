# coding: utf-8

from nose.tools import with_setup

import leancloud
from leancloud import User
from leancloud import Query

__author__ = 'asaka <lan@leancloud.rocks>'


def setup_func():
    leancloud.init(
        'pgk9e8orv8l9coak1rjht1avt2f4o9kptb0au0by5vbk9upb',
        master_key='azkuvukzlq3t38abdrgrwqqdcx9me6178ctulhd14wynfq1n',
    )


def destroy_func():
    users = Query(User).find()
    for user in users:
        print user
        user.destroy()


@with_setup(setup_func, destroy_func)
def test_sign_up():
    user = User()
    user.set('username', 'foo')
    user.set('password', 'bar')
    user.sign_up()
