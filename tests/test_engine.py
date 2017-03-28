# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import time
import json
import requests
import typing

from wsgi_intercept import requests_intercept
from wsgi_intercept import add_wsgi_intercept

import leancloud
from leancloud import Engine
from leancloud import cloudfunc
from leancloud.engine import authorization
from leancloud import LeanCloudError
from .request_generator import generate_request


__author__ = 'asaka <lan@leancloud.rocks>'

env = None  # type: typing.Dict[str, str]

TEST_APP_ID = os.environ['APP_ID']
TEST_APP_KEY = os.environ['APP_KEY']
TEST_MASTER_KEY = os.environ['MASTER_KEY']
sign_by_app_key = generate_request(TEST_APP_KEY)
sign_by_master_key = generate_request(TEST_MASTER_KEY, True)

NORMAL_HEADERS = {
    'x-avoscloud-application-id': TEST_APP_ID,
    'x-avoscloud-application-key': TEST_APP_KEY,
}


def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b'Hello LeanCloud']


engine = Engine(app)


def make_app():
    return engine


host, port = 'localhost', 80
url = 'http://{0}:{1}/'.format(host, port)


HookObject = leancloud.Object.extend('HookObject')


def setup():
    leancloud.client.USE_MASTER_KEY = None
    leancloud.client.APP_ID = None
    leancloud.client.APP_KEY = None
    leancloud.client.MASTER_KEY = None
    leancloud.init(TEST_APP_ID, TEST_APP_KEY, TEST_MASTER_KEY)
    authorization._ENABLE_TEST = True
    authorization.APP_ID = TEST_APP_ID
    authorization.APP_KEY = TEST_APP_KEY
    authorization.MASTER_KEY = TEST_MASTER_KEY

    requests_intercept.install()
    add_wsgi_intercept(host, port, make_app)

    @engine.define
    def hello(**params):
        return 'hello'

    @engine.define('fooBarBaz')
    def foo_bar_baz(**params):
        return 'yes'


def teardown():
    requests_intercept.uninstall()


def test_lean_engine_error():
    err = leancloud.LeanEngineError(233, 'llllleancloud')
    assert err.code == 233
    assert err.message == 'llllleancloud'
    err = leancloud.LeanEngineError('error messages')
    assert err.code == 400
    assert err.message == 'error messages'


def test_origin_response(): # type: () -> None
    resp = requests.get(url)
    assert resp.ok
    assert resp.content == b'Hello LeanCloud'


def test_compatibility(): # type: () -> None
    requests.get(url + '/1/functions/hello')
    assert '_app_params' in authorization.current_environ

    requests.get(url + '/1.1/functions/hello')
    assert '_app_params' in authorization.current_environ


def test_app_params_1(): # type: () -> None
    requests.get(url + '/__engine/1/functions/hello')
    assert '_app_params' in authorization.current_environ


def test_app_params_2(): # type: () -> None
    requests.get(url + '/__engine/1/functions/hello', headers={
        'x-avoscloud-application-id': 'foo',
        'x-avoscloud-application-key': 'bar',
        'x-avoscloud-session-token': 'baz',
    })
    env = authorization.current_environ
    assert env['_app_params']['id'] == 'foo'
    assert env['_app_params']['key'] == 'bar'
    assert env['_app_params']['session_token'] == 'baz'


def test_app_params_3(): # type: () -> None
    requests.get(url + '/__engine/1/functions/hello', headers={
        'x-avoscloud-request-sign': sign_by_app_key
    })
    env = authorization.current_environ
    assert env['_app_params']['key'] == TEST_APP_KEY


def test_app_params_4(): # type: () -> None
    requests.get(url + '/__engine/1/functions/hello', headers={
        'x-avoscloud-request-sign': sign_by_master_key
    })
    env = authorization.current_environ
    assert env['_app_params']['master_key'] == TEST_MASTER_KEY


def test_app_params_5(): # type: () -> None
    requests.get(url + '/__engine/1/functions/hello', headers={
        'x-avoscloud-application-id': 'foo',
        'x-avoscloud-master-key': 'bar',
    })
    env = authorization.current_environ
    assert env['_app_params']['id'] == 'foo'
    assert env['_app_params']['master_key'] == 'bar'


def test_short_app_params_1(): # type: () -> None
    requests.get(url + '/__engine/1/functions/hello', headers={
        'x-lc-id': 'foo',
        'x-lc-key': 'bar',
        'x-lc-session': 'baz',
    })
    env = authorization.current_environ
    assert env['_app_params']['id'] == 'foo'
    assert env['_app_params']['key'] == 'bar'
    assert env['_app_params']['master_key'] is None
    assert env['_app_params']['session_token'] == 'baz'


def test_short_app_params_2(): # type: () -> None
    requests.get(url + '/__engine/1/functions/hello', headers={
        'x-lc-id': 'foo',
        'x-lc-key': 'bar,master',
        'x-lc-session': 'baz',
    })
    env = authorization.current_environ
    assert env['_app_params']['id'] == 'foo'
    assert env['_app_params']['key'] is None
    assert env['_app_params']['master_key'] == 'bar'
    assert env['_app_params']['session_token'] == 'baz'


def test_short_app_params_3(): # type: () -> None
    requests.get(url + '/__engine/1/functions/hello', headers={
        'x-lc-sign': sign_by_app_key
    })
    env = authorization.current_environ
    assert env['_app_params']['key'] == TEST_APP_KEY
    assert env['_app_params']['master_key'] is None


def test_short_app_params_4(): # type: () -> None
    requests.get(url + '/__engine/1/functions/hello', headers={
        'x-lc-sign': sign_by_master_key
    })
    env = authorization.current_environ
    assert env['_app_params']['key'] is None
    assert env['_app_params']['master_key'] == TEST_MASTER_KEY


def test_body_params(): # type: () -> None
    requests.get(url + '/__engine/1/functions/hello', headers={
        'Content-Type': 'text/plain',
    }, data=json.dumps({
        '_ApplicationId': 'foo',
        '_ApplicationKey': 'bar',
        '_MasterKey': 'baz',
        '_SessionToken': 'qux',
    }))
    env = authorization.current_environ
    assert env['_app_params']['id'] == 'foo'
    assert env['_app_params']['key'] == 'bar'
    assert env['_app_params']['master_key'] == 'baz'
    assert env['_app_params']['session_token'] == 'qux'


def test_authorization_1(): # type: () -> None
    response = requests.get(url + '/__engine/1/functions/hello', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    })
    assert response.ok
    assert response.json() == {u'result': u'hello'}


def test_authorization_2(): # type: () -> None
    response = requests.get(url + '/__engine/1/functions/hello', headers={
        'x-lc-id': TEST_APP_ID,
        'x-lc-key': TEST_MASTER_KEY,
    })
    assert response.ok
    assert response.json() == {u'result': u'hello'}


def test_authorization_3(): # type: () -> None
    response = requests.get(url + '/__engine/1/functions/hello', headers={
        'x-avoscloud-application-id': 'foo',
        'x-avoscloud-application-key': 'bar',
    })
    assert response.status_code == 401


def test_register_cloud_func(): # type: () -> None
    @engine.define
    def ping(**params):
        assert params == {"foo": ["bar", "baz"]}
        return 'pong'

    response = requests.post(url + '/__engine/1/functions/ping', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    }, json={'foo': ['bar', 'baz']})
    assert response.ok
    assert response.json() == {u'result': u'pong'}

    # test run in local
    assert cloudfunc.run.local('ping', foo=['bar', 'baz']) == 'pong'


def test_cloud_func_name_alias(): # type: () -> None
    response = requests.get(url + '/__engine/1/functions/fooBarBaz', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    })
    assert response.ok
    assert response.json() == {u'result': u'yes'}


def test_realtime_cloud_func(): # type: () -> None
    @engine.define
    def _messageReceived():
        pass
    try:
        cloudfunc.run.local('_messageReceived', __sign='321,xxx')
    except leancloud.LeanEngineError as e:
        assert e.code == 401
    else:
        raise AssertionError
    response = requests.post(url + '/__engine/1/functions/_messageReceived', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    }, json={'foo': ['bar', 'baz'], '__sign': '123,xxx'})
    assert response.status_code == 401

    timestamp = int(time.time() * 1000)
    cloudfunc.run.local('_messageReceived', __sign=leancloud.utils.sign_hook('_messageReceived', TEST_MASTER_KEY, timestamp))


def test_on_verified(): # type: () -> None
    @engine.on_verified('sms')
    def on_sms_verified(user):
        assert isinstance(user, leancloud.User)
        assert user.id == 'xxx'

    timestamp = int(time.time() * 1000)
    response = requests.post(url + '/__engine/1/functions/onVerified/sms', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    }, json={'object': {'__sign': '123,xxx'}})
    assert response.status_code == 401
    response = requests.post(url + '/__engine/1/functions/onVerified/sms', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    }, json={
        'object': {
            'objectId': 'xxx',
            '__sign': leancloud.utils.sign_hook('__on_verified_sms', TEST_MASTER_KEY, timestamp),
        },
    })
    assert response.ok


def test_rpc_call(): # type: () -> None
    # test unsaved object
    @engine.define
    def rpc_unsaved(**params):
        result = leancloud.Object.create('Xxx', foo=['bar', 'baz'])
        return result

    obj = cloudfunc.rpc.local('rpc_unsaved')
    assert isinstance(obj, leancloud.Object)
    assert obj.get('foo') == ['bar', 'baz']

    # tewst saved object
    @engine.define
    def rpc_saved(**params):
        result = leancloud.Object.create('Xxx', foo=['bar', 'baz'])
        result.save()
        return result

    obj = cloudfunc.rpc.local('rpc_saved')
    assert isinstance(obj, leancloud.Object)
    assert obj.get('foo') == ['bar', 'baz']
    obj.destroy()

    # test object list
    @engine.define
    def rpc_list(**params):
        objs = [
            leancloud.Object.create('Xxx', foo=['bar']),
            leancloud.Object.create('xXX', foo=['baz']),
        ]
        objs[0].save()
        return objs

    objs = cloudfunc.rpc.local('rpc_list')
    assert isinstance(objs, list)
    assert objs[0].get('foo') == ['bar']
    assert objs[1].get('foo') == ['baz']
    objs[0].destroy()



def test_before_save_hook(): # type: () -> None
    @engine.before_save('HookObject')
    def before_hook_object_save(obj):
        assert obj.has('__before')
        obj.set('beforeSaveHookInserted', True)

    response = requests.post(url + '/__engine/1/functions/HookObject/beforeSave', json={
        'object': {'clientValue': 'blah'}
    }, headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    })
    assert response.ok
    assert response.json()['beforeSaveHookInserted'] == True
    assert response.json()['clientValue'] == 'blah'
    assert '__before' in response.json()


def test_after_save_hook(): # type: () -> None
    @engine.after_save('HookObject')
    def after_hook_object_save(obj):
        assert obj.has('__after')

    response = requests.post(url + '/__engine/1/functions/HookObject/afterSave', json={
        'object': {'clientValue': 'blah'}
    }, headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    })
    assert response.ok
    assert response.json() == {'result': 'ok'}


def test_before_update_hook(): # type: () -> None
    @engine.before_update('HookObject')
    def before_hook_object_update(obj):
        assert obj.updated_keys == ['clientValue']

    response = requests.post(url + '/__engine/1/functions/HookObject/beforeUpdate', json={
        'object': {'clientValue': 'blah', '__updateKeys': ['clientValue']}
    }, headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    })
    assert response.ok


def test_before_delete_hook(): # type: () -> None
    @engine.before_delete('HookObject')
    def before_hook_object_delete(obj):
        pass

    response = requests.post(url + '/__engine/1/functions/HookObject/beforeDelete', json={
        'object': {}
    }, headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    })
    assert response.ok
    assert response.json() == {}


def test_on_login(): # type: () -> None
    @engine.on_login
    def on_login(user):
        assert isinstance(user, leancloud.User)

    timestamp = int(time.time() * 1000)
    response = requests.post(url + '/__engine/1.1/functions/_User/onLogin', json={
        'object': {
            '__sign': leancloud.utils.sign_hook('__on_login__User', TEST_MASTER_KEY, timestamp),
        },
    }, headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    })
    assert response.ok


def test_insight(): # type: () -> None
    @engine.on_insight('end')
    def on_insight_end(ok, data):
        assert ok is False
        assert data == {
            "id": u"job id",
            "status": u"OK/ERROR",
            "message": u"当  status 为 ERROR 时的错误消息"
        }

    timestamp = int(time.time() * 1000)
    response = requests.post(url + '/__engine/1/functions/BigQuery/onComplete', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    }, json={
        "id": u"job id",
        "status": u"OK/ERROR",
        "message": u"当  status 为 ERROR 时的错误消息",
        '__sign': leancloud.utils.sign_hook('__on_complete_bigquery_job', TEST_MASTER_KEY, timestamp),
    })
    assert response.ok


def test_client(): # type: () -> None
    leancloud.init(os.environ['APP_ID'], os.environ['APP_KEY'])
    assert cloudfunc.run('add', a=1, b=2) == 3


def test_request_sms_code(): # type: () -> None
    if leancloud.client.REGION == 'US':
        return
    leancloud.init(os.environ['APP_ID'], master_key=os.environ['MASTER_KEY'])
    try:
        cloudfunc.request_sms_code('13111111111')
    except LeanCloudError as e:
        # 短信发送过于频繁或者欠费或者关闭短信功能
        if e.code in (601, 160, 119):
            pass
        else:
            raise e


def test_current_user(): # type: () -> None
    leancloud.init(os.environ['APP_ID'], master_key=os.environ['MASTER_KEY'])
    saved_user = leancloud.User()
    saved_user.set('username', 'user{0}'.format(int(time.time())))
    saved_user.set('password', 'password')
    saved_user.set_email('{0}@leancloud.rocks'.format(int(time.time())))
    saved_user.sign_up()
    session_token = saved_user.get_session_token()

    @engine.define
    def current_user():
        user = engine.current_user
        TestCurrentUser = leancloud.Object.extend('TestCurrentUser')
        o = TestCurrentUser()
        o.set('user', user)
        o.set({'yetAnotherUser': user})
        o.save()

        TestCurrentUser.query.equal_to('user', user).find()
        assert user.get('username') == saved_user.get('username')

        # test current
        assert engine.current.session_token == session_token
        assert user.get('username') is engine.current.user.get('username')
        assert 'remote_address' in engine.current.meta

    response = requests.get(url + '/__engine/1/functions/current_user', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
        'x-avoscloud-session-token': session_token,
    })
    assert response.status_code == 200

    @engine.before_save('Xxx')
    def before_xxx_save(xxx):
        assert engine.current_user.get('username') == saved_user.get('username')

    response = requests.post(url + '/__engine/1/functions/Xxx/beforeSave', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    }, json={'object': {}, 'user': {'username': saved_user.get('username')}})
    assert response.status_code == 200

    # cleanup
    saved_user.destroy()
