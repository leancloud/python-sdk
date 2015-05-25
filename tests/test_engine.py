# coding: utf-8

import requests

from wsgi_intercept import requests_intercept, add_wsgi_intercept


import leancloud
from leancloud import Engine
from leancloud import cloudfunc
from leancloud.engine import authorization


__author__ = 'asaka <lan@leancloud.rocks>'

env = None

TEST_APP_ID = 'mdx1l0uh1p08tdpsk8ffn4uxjh2bbhl86rebrk3muph08qx7'
TEST_APP_KEY = 'n35a5fdhawz56y24pjn3u9d5zp9r1nhpebrxyyu359cq0ddo'
TEST_MASTER_KEY = 'h2ln3ffyfzysxmkl4p3ja7ih0y6sq5knsa2j0qnm1blk2rn2'

NORMAL_HEADERS = {
    'x-avoscloud-application-id': TEST_APP_ID,
    'x-avoscloud-application-key': TEST_APP_KEY,
}


def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello LeanCloud']


engine = Engine(app)


def make_app():
    return engine


host, port = 'localhost', 80
url = 'http://{0}:{1}/'.format(host, port)


def setup():
    leancloud.init(TEST_APP_ID, TEST_APP_KEY)
    authorization._ENABLE_TEST = True
    authorization.APP_ID = TEST_APP_ID
    authorization.APP_KEY = TEST_APP_KEY
    authorization.MASTER_KEY = TEST_MASTER_KEY

    requests_intercept.install()
    add_wsgi_intercept(host, port, make_app)

    @engine.define
    def hello(**params):
        return 'hello'


def teardown():
    requests_intercept.uninstall()


def test_origin_response():
    resp = requests.get(url)
    assert resp.ok
    assert resp.content == 'Hello LeanCloud'


def test_compatibility():
    requests.get(url + '/1/functions/hello')
    assert '_app_params' in authorization.current_environ

    requests.get(url + '/1.1/functions/hello')
    assert '_app_params' in authorization.current_environ


def test_app_params_1():
    requests.get(url + '/__engine/1/functions/hello')
    assert '_app_params' in authorization.current_environ


def test_app_params_2():
    resp = requests.get(url + '/__engine/1/functions/hello', headers={
        'x-avoscloud-application-id': 'foo',
        'x-avoscloud-application-key': 'bar',
        'x-avoscloud-session-token': 'baz',
    })
    env = authorization.current_environ
    assert env['_app_params']['id'] == 'foo'
    assert env['_app_params']['key'] == 'bar'
    assert env['_app_params']['session_token'] == 'baz'


def test_app_params_3():
    requests.get(url + '/__engine/1/functions/hello', headers={
        'x-avoscloud-request-sign': '28ad0513f8788d58bb0f7caa0af23400,1389085779854'
    })
    env = authorization.current_environ
    assert env['_app_params']['key'] == 'n35a5fdhawz56y24pjn3u9d5zp9r1nhpebrxyyu359cq0ddo'


def test_app_params_4():
    requests.get(url + '/__engine/1/functions/hello', headers={
        'x-avoscloud-request-sign': 'c884fe684c17c972eb4e33bc8b29cb5b,1389085779854,master'
    })
    env = authorization.current_environ
    assert env['_app_params']['key'] == 'h2ln3ffyfzysxmkl4p3ja7ih0y6sq5knsa2j0qnm1blk2rn2'


def test_authorization_1():
    response = requests.get(url + '/__engine/1/functions/hello', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    })
    assert response.ok
    assert response.json() == {u'result': u'hello'}


def test_authorization_2():
    response = requests.get(url + '/__engine/1/functions/hello', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_MASTER_KEY,
    })
    assert response.ok
    assert response.json() == {u'result': u'hello'}


def test_authorization_3():
    response = requests.get(url + '/__engine/1/functions/hello', headers={
        'x-avoscloud-application-id': 'foo',
        'x-avoscloud-application-key': 'bar',
    })
    assert response.status_code == 401


def test_register_cloud_func():
    @engine.define
    def ping(**params):
        assert params == {"foo": ["bar", "baz"]}
        return 'pong'

    response = requests.post(url + '/__engine/1/functions/ping', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    }, json={'foo': ['bar', 'baz']})
    assert response.ok
    print response.json() == {u'result': u'pong'}


def test_client():
    leancloud.init('pgk9e8orv8l9coak1rjht1avt2f4o9kptb0au0by5vbk9upb', 'hi4jsm62kok2qz2w2qphzryo564rzsrucl2czb0hn6ogwwnd')
    assert cloudfunc.run('add', a=1, b=2) == 3
