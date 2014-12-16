# coding: utf-8

from StringIO import StringIO

from leancloud import File
from leancloud import ACL

__author__ = 'asaka'


def test_basic():
    s = StringIO('blah blah blah')
    f = File('blah', s)
    assert f.name == 'blah'
    assert f._metadata['size'] == 14
    assert f._guessed_type == 'text/plain'


def test_create_with_url():
    f = File.create_with_url('xxx', 'http://www.leancloud.cn')
    assert f.url == 'http://www.leancloud.cn'


def test_create_without_data():
    f = File.create_without_data(123)
    assert f.id == 123


def test_acl():
    acl = ACL()
    f = File('blah', buffer('xxx'))
    f.set_acl(acl)
    assert f.get_acl() == acl
