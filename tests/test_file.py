# coding: utf-8

import os

from StringIO import StringIO
from nose.tools import with_setup

import requests

import leancloud
from leancloud import File
from leancloud import ACL

__author__ = 'asaka'


def setup_func():
    leancloud.init(
        os.environ['APP_ID'],
        os.environ['APP_KEY']
    )


def test_basic():
    s = StringIO('blah blah blah')
    f = File('Blah', s)
    assert f.name == 'Blah'
    assert f._metadata['size'] == 14
    assert f._type == 'text/plain'


def test_create_with_url():
    f = File.create_with_url('xxx', 'http://www.lenna.org/full/len_std.jpg')
    assert f.url == 'http://www.lenna.org/full/len_std.jpg'


def test_create_without_data():
    f = File.create_without_data(123)
    assert f.id == 123


def test_acl():
    acl = ACL()
    f = File('Blah', buffer('xxx'))
    f.set_acl(acl)
    assert f.get_acl() == acl


@with_setup(setup_func)
def test_save():
    f = File('Blah', buffer('xxx'))
    f.save()
    assert f.id


@with_setup(setup_func)
def test_save_external():
    f = File.create_with_url('lenna.jpg', 'http://www.lenna.org/full/len_std.jpg')
    f.save()
    assert f.id


@with_setup(setup_func)
def test_thumbnail():
    r = requests.get('http://www.lenna.org/full/len_std.jpg')
    b = buffer(r.content)
    f = File('Lenna2.jpg', b)
    f.save()
    assert f.id

    url = f.get_thumbnail_url(100, 100)
    assert url.endswith('?imageView/2/w/100/h/100/q/100/format/png')
