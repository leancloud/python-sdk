# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from nose.tools import eq_
from nose.tools import with_setup

import leancloud


__author__ = 'asaka <lan@leancloud.rocks>'


def setup_func():
    leancloud.client.USE_MASTER_KEY = None
    leancloud.client.APP_ID = None
    leancloud.client.APP_KEY = None
    leancloud.client.MASTER_KEY = None
    leancloud.init(
        os.environ['APP_ID'],
        master_key=os.environ['MASTER_KEY']
    )

def test_init(): # type: () -> None
    acl = leancloud.ACL()
    role = leancloud.Role('xxx', acl)
    assert role
    assert role.get_name() == 'xxx'
    assert role.get_acl() == acl


def test_init_with_default_acl(): # type: () -> None
    role = leancloud.Role('qux')
    assert role
    assert role.get_name() == 'qux'
    acl = role.get_acl()
    assert acl.dump() == {'*': {'read': True}}


@with_setup(setup=setup_func)
def test_role_query(): # type: () -> None
    roles = leancloud.Query(leancloud.Role).limit(1000).find()
    leancloud.Object.destroy_all(roles)

    role = leancloud.Role('test_role')
    role.save()

    eq_(leancloud.Query(leancloud.Role).count(), 1)
    eq_(leancloud.Query(leancloud.Role).find()[0].get_name(), role.get_name()) # type: ignore
