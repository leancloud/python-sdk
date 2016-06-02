# coding: utf-8

import json
import logging
import traceback
import functools

import leancloud
from werkzeug.wrappers import Response
from werkzeug.routing import Map
from werkzeug.routing import Rule
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotAcceptable

from . import context
from leancloud._compat import to_native


__author__ = 'asaka <lan@leancloud.rocks>'

logger = logging.getLogger('leancloud.cloudcode.cloudcode')

user = context.local('user')


class LeanEngineError(Exception):
    def __init__(self, code=1, message='error'):
        self.code = code
        self.message = message


class LeanEngineApplication(object):
    def __init__(self):
        self.url_map = Map([
            Rule('/__engine/1/functions/<func_name>', endpoint='cloud_function'),
            Rule('/__engine/1.1/functions/<func_name>', endpoint='cloud_function'),
            Rule('/__engine/1/call/<func_name>', endpoint='rpc_function'),
            Rule('/__engine/1.1/call/<func_name>', endpoint='rpc_function'),
            Rule('/__engine/1/functions/BigQuery/<event>', endpoint='on_bigquery'),
            Rule('/__engine/1.1/functions/BigQuery/<event>', endpoint='on_bigquery'),
            Rule('/__engine/1.1/functions/_User/onLogin', endpoint='on_login'),
            Rule('/__engine/1/functions/_User/onLogin', endpoint='on_login'),
            Rule('/__engine/1/functions/<class_name>/<hook_name>', endpoint='cloud_hook'),
            Rule('/__engine/1.1/functions/<class_name>/<hook_name>', endpoint='cloud_hook'),
            Rule('/__engine/1/functions/onVerified/<verify_type>', endpoint='on_verified'),
            Rule('/__engine/1.1/functions/onVerified/<verify_type>', endpoint='on_verified'),
            Rule('/__engine/1/functions/_ops/metadatas', endpoint='ops_meta_data'),
            Rule('/__engine/1.1/functions/_ops/metadatas', endpoint='ops_meta_data'),

            Rule('/1/functions/<func_name>', endpoint='cloud_function'),
            Rule('/1.1/functions/<func_name>', endpoint='cloud_function'),
            Rule('/1/call/<func_name>', endpoint='rpc_function'),
            Rule('/1.1/call/<func_name>', endpoint='rpc_function'),
            Rule('/1/functions/BigQuery/<event>', endpoint='on_bigquery'),
            Rule('/1.1/functions/BigQuery/<event>', endpoint='on_bigquery'),
            Rule('/1.1/functions/_User/onLogin', endpoint='on_login'),
            Rule('/1/functions/_User/onLogin', endpoint='on_login'),
            Rule('/1/functions/<class_name>/<hook_name>', endpoint='cloud_hook'),
            Rule('/1.1/functions/<class_name>/<hook_name>', endpoint='cloud_hook'),
            Rule('/1/functions/onVerified/<verify_type>', endpoint='on_verified'),
            Rule('/1.1/functions/onVerified/<verify_type>', endpoint='on_verified'),
            Rule('/1/functions/_ops/metadatas', endpoint='ops_meta_data'),
            Rule('/1.1/functions/_ops/metadatas', endpoint='ops_meta_data'),
        ])

    def __call__(self, environ, start_response):
        self.process_session(environ)
        request = environ['leanengine.request']

        response = self.dispatch_request(request)

        return response(environ, start_response)

    @classmethod
    def process_session(cls, environ):
        if environ['_app_params']['session_token'] not in (None, ''):
            session_token = environ['_app_params']['session_token']
            user = leancloud.User.become(session_token)
            context.local.user = user
            return

        request = environ['leanengine.request']
        try:
            # the JSON object must be str, not 'bytes' for 3.x.
            data = json.loads(to_native(request.get_data()))
        except ValueError:
            context.local.user = None
            return

        if 'user' in data and data['user']:
            user = leancloud.User()
            user._finish_fetch(data['user'], True)
            context.local.user = user
            return

        context.local.user = None

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
        except HTTPException as e:
            return e

        # the JSON object must be str, not 'bytes' for 3.x.
        params = to_native(request.get_data())
        values['params'] = json.loads(params) if params != '' else {}

        try:
            if endpoint == 'cloud_function':
                result = {'result': dispatch_cloud_func(decode_object=False, **values)}
            elif endpoint == 'rpc_function':
                result = {'result': dispatch_cloud_func(decode_object=True, **values)}
            elif endpoint == 'cloud_hook':
                result = dispatch_cloud_hook(**values)
            elif endpoint == 'on_verified':
                result = {'result': dispatch_on_verified(**values)}
            elif endpoint == 'on_login':
                result = {'result': dispatch_on_login(**values)}
            elif endpoint == 'ops_meta_data':
                result = {'result': dispatch_ops_meta_data()}
            elif endpoint == 'on_bigquery':
                result = {'result': dispatch_on_bigquery(**values)}
            else:
                raise ValueError    # impossible
            return Response(json.dumps(result), mimetype='application/json')
        except LeanEngineError as e:
            return Response(
                json.dumps({'code': e.code, 'error': e.message}),
                status=400,
                mimetype='application/json'
            )
        except Exception:
            print(traceback.format_exc())
            return Response(
                json.dumps({'code': 141, 'error': 'Cloud Code script had an error.'}),
                status=500,
                mimetype='application/json'
            )


hook_name_mapping = {
    'beforeSave': '__before_save_for_',
    'afterSave': '__after_save_for_',
    'beforeUpdate': '__before_update_for_',
    'afterUpdate': '__after_update_for_',
    'beforeDelete': '__before_delete_for_',
    'afterDelete': '__after_delete_for_',
}

_cloud_codes = {}


def register_cloud_func(func):
    func_name = func.__name__
    if func_name in _cloud_codes:
        raise RuntimeError('cloud function: {0} is already registered'.format(func_name))
    _cloud_codes[func_name] = func
    return func


def dispatch_cloud_func(func_name, decode_object, params):
    # delete all keys in params which starts with low dash.
    # JS SDK may send it's app info with them.
    keys = params.keys()
    for key in keys:
        if key.startswith('_') and key != '__type':
            params.pop(key)

    if decode_object:
        params = leancloud.utils.decode('', params)

    func = _cloud_codes.get(func_name)
    if not func:
        raise LeanEngineError(code=404, message="cloud func named '{0}' not found.".format(func_name))

    logger.info("{0} is called!".format(func_name))

    result = func(**params)

    if decode_object:
        if isinstance(result, leancloud.Object):
            result = leancloud.utils.encode(result._dump())
        else:
            result = leancloud.utils.encode(result)

    return result


def register_cloud_hook(class_name, hook_name):
    # hack the hook name
    hook_name = hook_name_mapping[hook_name] + class_name

    if hook_name in _cloud_codes:
        raise RuntimeError('cloud hook {0} on class {1} is already registered'.format(hook_name, class_name))

    def new_func(func):
        _cloud_codes[hook_name] = func

    return new_func


before_save = functools.partial(register_cloud_hook, hook_name='beforeSave')

after_save = functools.partial(register_cloud_hook, hook_name='afterSave')

before_update = functools.partial(register_cloud_hook, hook_name='beforeUpdate')

after_update = functools.partial(register_cloud_hook, hook_name='afterUpdate')

before_delete = functools.partial(register_cloud_hook, hook_name='beforeDelete')

after_delete = functools.partial(register_cloud_hook, hook_name='afterDelete')


def dispatch_cloud_hook(class_name, hook_name, params):
    hook_name = hook_name_mapping[hook_name] + class_name
    if hook_name not in _cloud_codes:
        raise NotAcceptable

    obj = leancloud.Object.create(class_name)
    obj._finish_fetch(params['object'], True)

    if '__updateKeys' in params['object']:
       obj.updated_keys = params['object']['__updateKeys']

    if hook_name.startswith('__before'):
        if obj.has('__before'):
            obj.set('__before', obj.get('__before'))
        else:
            obj.disable_before_hook()
    elif hook_name.startswith('__after'):
        if obj.has('__after'):
            obj.set('__after', obj.get('__after'))
        else:
            obj.disable_after_hook()

    logger.info("{0}:{1} is called!".format(class_name, hook_name))

    func = _cloud_codes[hook_name]
    if not func:
        raise leancloud.LeanEngineError(code=404, message="cloud hook named '{0}' not found.".format(hook_name))

    func(obj)
    if hook_name.startswith('__after'):
        return {'result': 'ok'}
    elif hook_name.startswith('__before_delete_for'):
        return {}
    else:
        return obj.dump()


def register_on_verified(verify_type):
    if verify_type not in set(['sms', 'email']):
        raise RuntimeError('verify_type must be sms or email')

    func_name = '__on_verified_{0}'.format(verify_type)

    def new_func(func):
        if func_name in _cloud_codes:
            raise RuntimeError('on verified is already registered')
        _cloud_codes[func_name] = func
    return new_func


def dispatch_on_verified(verify_type, user):
    func = _cloud_codes.get(verify_type)
    if not func:
        return

    return func(user)


def register_on_login(func):
    func_name = '__on_login__User'

    if func_name in _cloud_codes:
        raise RuntimeError('on login is already registered')
    _cloud_codes[func_name] = func


def dispatch_on_login(params):
    func = _cloud_codes.get('__on_login__User')
    if not func:
        return

    user = leancloud.User()
    user._finish_fetch(params['object'], True)

    return func(user)


def dispatch_ops_meta_data():
    return list(_cloud_codes.keys())


def register_on_bigquery(event):
    if event == 'end':
        func_name = '__on_complete_bigquery_job'
    else:
        raise RuntimeError('event not support')

    def inner_func(func):
        if func_name in _cloud_codes:
            raise RuntimeError('on bigquery is already registered')
        _cloud_codes[func_name] = func
    return inner_func


def dispatch_on_bigquery(event, params):
    if event == 'onComplete':
        func_name = '__on_complete_bigquery_job'
    else:
        return

    func = _cloud_codes.get(func_name)
    if not func:
        return

    ok = True if params['status'] == 'OK' else False
    return func(ok, params)
