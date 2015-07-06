# coding: utf-8

import leancloud


__author__ = 'asaka <lan@leancloud.rocks>'


def test_init():
    acl = leancloud.ACL()
    role = leancloud.Role('xxx', acl)
    assert role
    assert role.get_name() == 'xxx'
    assert role.get_acl() == acl
