# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import io

import six

if six.PY2:
    from urlparse import urlparse
if six.PY3:
    from urllib.parse import urlparse

import requests
from nose.tools import with_setup  # type: ignore
from nose.tools import assert_raises  # type: ignore
from nose.tools import raises  # type: ignore

import leancloud
from leancloud import File, LeanCloudError
from leancloud import ACL

__author__ = "asaka"


def setup_func():
    leancloud.init(os.environ["APP_ID"], master_key=os.environ["MASTER_KEY"])


def setup_without_master_key():
    leancloud.init(os.environ["APP_ID"], os.environ["APP_KEY"])


def test_basic():  # type: () -> None
    def fn(s):
        f = File("Blah", s, mime_type="text/plain")
        assert f.name == "Blah"
        assert f._metadata["size"] == 14
        assert f.size == 14
        assert f._metadata["_checksum"] == "55e562bfee2bde4f9e71b8885eb5e303"

    b = b"blah blah blah"
    fn(io.BytesIO(b))
    fn(memoryview(b))

    import tempfile

    f = tempfile.SpooledTemporaryFile()
    f.write(b)
    fn(f)

    if six.PY2:
        import StringIO
        import cStringIO

        fn(StringIO.StringIO(b))
        fn(cStringIO.StringIO(b))
        fn(buffer(b))  # noqa: F821

    if six.PY3:
        fn(b)

def test_create_with_url():  # type: () -> None
    f = File.create_with_url(
        "xxx",
        u"http://i1.wp.com/leancloud.cn/images/static/default-avatar.png",
        meta_data={},
    )
    assert f._url == "http://i1.wp.com/leancloud.cn/images/static/default-avatar.png"
    assert f.url is None


def test_create_without_data():  # type: () -> None
    f = File.create_without_data("a123")
    assert f.id == "a123"


def test_acl():  # type: () -> None
    acl_ = ACL()
    f = File("Blah", io.BytesIO(b"xxx"))
    assert_raises(TypeError, f.set_acl, "a")
    f.set_acl(acl_)
    assert f.get_acl() == acl_


@with_setup(setup_func)
def test_save():  # type: () -> None
    user = leancloud.User()
    name = "user1_name"
    passwd = "password"
    try:
        user.login(name, passwd)
    except LeanCloudError as e:
        if e.code == 211:
            user.set_username(name)
            user.set_password(passwd)
            user.sign_up()
            user.login(name, passwd)

    f = File("Blah.txt", open("tests/sample_text.txt", "rb"))
    f.save()

    assert f.owner_id == user.id
    assert f.id
    assert f.name == "Blah.txt"
    assert f.mime_type == "text/plain"
    assert not f.url.endswith(".")
    assert f.created_at == f.updated_at


@with_setup(setup_func)
def test_save_with_specified_key():  # type: () -> None
    f = File("Blah.txt", open("tests/sample_text.txt", "rb"))
    user_specified_key = "abc"
    f.key = user_specified_key
    f.save()

    assert f.id
    assert f.created_at == f.updated_at
    assert f.name == "Blah.txt"
    assert f.mime_type == "text/plain"
    path = urlparse(f.url).path
    if path.startswith("/avos-cloud-"):  # old school aws s3 file url
        assert path.split("/")[2] == user_specified_key
    elif f.url.startswith("https://lc-gluttony"):  # new aws s3 gluttony bucket
        gluttony_path = "/" + os.environ["APP_ID"][0:12] + "/" + user_specified_key
        assert path == gluttony_path
    else:
        assert path == "/" + user_specified_key


@with_setup(setup_without_master_key)
def test_save_with_specified_key_but_without_master_key():  # type: () -> None
    f = File("Blah.txt", open("tests/sample_text.txt", "rb"))
    f.key = "abc"
    try:
        f.save()
    except LeanCloudError as e:
        if e.code == 1 and e.error.startswith("Unsupported file key"):
            pass


@with_setup(setup_func)
def test_query():  # type: () -> None
    files = leancloud.Query("File").find()
    for f in files:
        assert isinstance(f, File)
        assert f.id
        assert f.url
        assert f.name
        assert f.metadata
        assert f.created_at == f.updated_at
        if f.metadata.get("__source") == 'external':
            assert f.url
        else:
            assert f.key

    assert isinstance(leancloud.File.query.first(), File)

@with_setup(setup_func)
def test_scan():  # type: () -> None
    files = leancloud.Query("File").scan()
    for f in files:
        assert isinstance(f, File)
        assert f.created_at == f.updated_at
        assert f.name
        assert f.metadata
        if f.metadata.get("__source") == 'external':
            assert f.url
        else:
            assert f.key
        

@with_setup(setup_func)
def test_save_external():  # type: () -> None
    file_name = "lenna.jpg"
    file_url = "http://i1.wp.com/leancloud.cn/images/static/default-avatar.png"
    f = File.create_with_url(file_name, file_url)
    f.save()
    assert f.id
    assert f.created_at == f.updated_at
    file_on_cloud = File.create_without_data(f.id)
    file_on_cloud.fetch()
    assert file_on_cloud.name == file_name
    assert file_on_cloud.url == file_url


@raises(ValueError)
def test_thumbnail_url_erorr():  # type: () -> None
    f = File.create_with_url("xx", "")
    f.get_thumbnail_url(100, 100)


@with_setup(setup_func)
@raises(ValueError)
def test_thumbnail_size_erorr():  # type: () -> None
    r = requests.get("http://i1.wp.com/leancloud.cn/images/static/default-avatar.png")
    b = io.BytesIO(r.content)
    f = File("Lenna2.jpg", b)
    f.save()
    assert f.id

    f.get_thumbnail_url(-1, -1)
    f.get_thumbnail_url(1, 1, quality=110)


@with_setup(setup_func)
def test_thumbnail():  # type: () -> None
    r = requests.get("http://i1.wp.com/leancloud.cn/images/static/default-avatar.png")
    b = io.BytesIO(r.content)
    f = File("Lenna2.jpg", b)
    f.save()
    assert f.id

    url = f.get_thumbnail_url(100, 100)
    assert url.endswith("?imageView/2/w/100/h/100/q/100/format/png")


@with_setup(setup_func)
def test_destroy():  # type: () -> None
    r = requests.get("http://i1.wp.com/leancloud.cn/images/static/default-avatar.png")
    b = io.BytesIO(r.content)
    f = File("Lenna2.jpg", b)
    f.save()
    assert f.id
    f.destroy()


@with_setup(setup_func)
def test_file_callback():  # type: () -> None
    d = {}

    def noop(token, *args, **kwargs):
        d["token"] = token

    f = File("xxx", io.BytesIO(b"xxx"))
    f._save_to_s3 = noop
    f._save_to_qiniu = noop
    f._save_to_qcloud = noop
    f.save()
    f._save_callback(d["token"], False)

    # time.sleep(3)
    # File should be deleted by API server
    # assert_raises(leancloud.LeanCloudError, File.query().get, f.id)


@with_setup(setup_func)
def test_fetch():  # type: () -> None
    r = requests.get("http://i1.wp.com/leancloud.cn/images/static/default-avatar.png")
    b = io.BytesIO(r.content)
    f = File("Lenna2.jpg", b)
    f.metadata["foo"] = "bar"
    f.save()
    fetched = File.create_without_data(f.id)
    fetched.fetch()

    normalized_f_url = f.url.split("/")[-1]
    normalized_fetched_url = f.url.split("/")[-1]

    assert fetched.id == f.id
    assert fetched.metadata == f.metadata
    assert fetched.name == f.name
    assert fetched.size == f.size
    assert fetched.url == f.url or normalized_fetched_url == normalized_f_url
    f.destroy()


def test_checksum():  # type: () -> None
    f = File("Blah", open("tests/sample_text.txt", "rb"))
    assert f._metadata["_checksum"] == "d0588d95e45eed70745ffabdf0b18acd"
