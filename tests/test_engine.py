# coding: utf-8

import os
import requests

from wsgi_intercept import requests_intercept, add_wsgi_intercept


import leancloud
from leancloud import Engine
from leancloud import cloudfunc
from leancloud.engine import authorization
from request_generator import *


__author__ = 'asaka <lan@leancloud.rocks>'

env = None

TEST_APP_ID = os.environ['appid']
TEST_APP_KEY = os.environ['appkey']
TEST_MASTER_KEY = os.environ['masterKey']
param_3_request = generate_request(TEST_APP_KEY)
param_4_request = generate_request(TEST_MASTER_KEY, True)

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
        'x-avoscloud-request-sign': param_3_request
    })
    env = authorization.current_environ
    assert env['_app_params']['key'] == TEST_APP_KEY


def test_app_params_4():
    requests.get(url + '/__engine/1/functions/hello', headers={
        'x-avoscloud-request-sign': param_4_request
    })
    env = authorization.current_environ
    assert env['_app_params']['key'] == TEST_MASTER_KEY


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


def test_bigquery():
    @engine.on_bigquery('end')
    def on_bigquery_end(ok, data):
        assert ok is False
        assert data == {
            "id": u"job id",
            "status": u"OK/ERROR",
            "message": u"当  status 为 ERROR 时的错误消息"
        }

    response = requests.post(url + '/__engine/1/functions/BigQuery/onComplete', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    }, json={
        "id": u"job id",
        "status": u"OK/ERROR",
        "message": u"当  status 为 ERROR 时的错误消息"
    })
    assert response.ok


def test_client():
    leancloud.init(os.environ['appid'], os.environ['appkey'])
    assert cloudfunc.run('add', a=1, b=2) == 3


def test_request_sms_code():
    leancloud.init(os.environ['appid'], master_key=os.environ['masterKey'])
    cloudfunc.request_sms_code('13111111111')
