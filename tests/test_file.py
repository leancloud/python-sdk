# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from nose.tools import with_setup  # type: ignore
from nose.tools import assert_raises  # type: ignore
from nose.tools import raises  # type: ignore

import requests

import leancloud
from leancloud import File
from leancloud import ACL
from leancloud._compat import PY2
from leancloud._compat import BytesIO
from leancloud._compat import buffer_type

__author__ = 'asaka'


def setup_func():
    leancloud.init(
        os.environ['APP_ID'],
        master_key=os.environ['MASTER_KEY']
    )


def test_basic():  # type: () -> None
    s = BytesIO(b'blah blah blah')
    if PY2:
        import cStringIO  # type: ignore
        s1 = cStringIO.StringIO()
        s1.write('blah blah blah')
    else:
        s1 = s
    f1 = File('Blah', s, mime_type='text/plain')
    f2 = File('Blah', s1, type_='text/plain')
    for f in (f1, f2):
        assert f.name == 'Blah'
        assert f._metadata['size'] == 14
        assert f.size == 14


def test_create_with_url():  # type: () -> None
    f = File.create_with_url('xxx', u'http://i1.wp.com/leancloud.cn/images/static/default-avatar.png', meta_data={})
    assert f.url == 'http://i1.wp.com/leancloud.cn/images/static/default-avatar.png'


def test_create_without_data():  # type: () -> None
    f = File.create_without_data('a123')
    assert f.id == 'a123'


def test_acl():  # type: () -> None
    acl_ = ACL()
    f = File('Blah', buffer_type(b'xxx'))
    assert_raises(TypeError, f.set_acl, 'a')
    f.set_acl(acl_)
    assert f.get_acl() == acl_


@with_setup(setup_func)
def test_save():  # type: () -> None
    user = leancloud.User()
    user.login('user1_name', 'password')

    f = File('Blah.txt', buffer_type(b'xxx'))
    f.save()

    assert f.owner_id == user.id
    assert f.id
    assert f.name == 'Blah.txt'
    assert f.mime_type == 'text/plain'
    assert not f.url.endswith('.')


@with_setup(setup_func)
def test_query():  # type: () -> None
    files = leancloud.Query('File').find()
    for f in files:
        assert isinstance(f, File)
        assert f.url
        assert f.name
        assert f.metadata

    assert isinstance(leancloud.File.query.first(), File)


@with_setup(setup_func)
def test_save_external():  # type: () -> None
    f = File.create_with_url('lenna.jpg', 'http://i1.wp.com/leancloud.cn/images/static/default-avatar.png')
    f.save()
    assert f.id


@raises(ValueError)
def test_thumbnail_url_erorr():  # type: () -> None
    f = File.create_with_url('xx', '')
    f.get_thumbnail_url(100, 100)


@with_setup(setup_func)
@raises(ValueError)
def test_thumbnail_size_erorr():  # type: () -> None
    r = requests.get('http://i1.wp.com/leancloud.cn/images/static/default-avatar.png')
    b = buffer_type(r.content)
    f = File('Lenna2.jpg', b)
    f.save()
    assert f.id

    f.get_thumbnail_url(-1, -1)
    f.get_thumbnail_url(1, 1, quality=110)


@with_setup(setup_func)
def test_thumbnail():  # type: () -> None
    r = requests.get('http://i1.wp.com/leancloud.cn/images/static/default-avatar.png')
    b = buffer_type(r.content)
    f = File('Lenna2.jpg', b)
    f.save()
    assert f.id

    url = f.get_thumbnail_url(100, 100)
    assert url.endswith('?imageView/2/w/100/h/100/q/100/format/png')


@with_setup(setup_func)
def test_destroy():  # type: () -> None
    r = requests.get('http://i1.wp.com/leancloud.cn/images/static/default-avatar.png')
    b = buffer_type(r.content)
    f = File('Lenna2.jpg', b)
    f.save()
    assert f.id
    f.destroy()


@with_setup(setup_func)
def test_file_callback():  # type: () -> None
    d = {}

    def noop(token, *args, **kwargs):
        d['token'] = token

    f = File('xxx', buffer_type(b'xxx'))
    f._save_to_s3 = noop
    f._save_to_qiniu = noop
    f._save_to_qcloud = noop
    f.save()
    f._save_callback(d['token'], False)

    # time.sleep(3)
    # File should be deleted by API server
    # assert_raises(leancloud.LeanCloudError, File.query().get, f.id)


@with_setup(setup_func)
def test_fetch():  # type: () -> None
    r = requests.get('http://i1.wp.com/leancloud.cn/images/static/default-avatar.png')
    b = buffer_type(r.content)
    f = File('Lenna2.jpg', b)
    f.metadata['foo'] = 'bar'
    f.save()
    fetched = File.create_without_data(f.id)
    fetched.fetch()
    assert fetched.id == f.id
    assert fetched.metadata == f.metadata
    assert fetched.name == f.name
    assert fetched.url == f.url
    assert fetched.size == f.size
    assert fetched.url == f.url
    f.destroy()


def test_checksum():  # type: () -> None
    f = File('Blah', open('tests/sample_text.txt', 'rb'))
    assert f._metadata['_checksum'] == 'd0588d95e45eed70745ffabdf0b18acd'
