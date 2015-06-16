# coding: utf-8

import json
import logging
import traceback
import functools

import leancloud
from werkzeug.wrappers import Request
from werkzeug.wrappers import Response
from werkzeug.routing import Map
from werkzeug.routing import Rule
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import NotAcceptable

from . import context


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
            Rule('/__engine/1/functions/BigQuery/<event>', endpoint='on_bigquery'),
            Rule('/__engine/1.1/functions/BigQuery/<event>', endpoint='on_bigquery'),
            Rule('/__engine/1/functions/<class_name>/<hook_name>', endpoint='cloud_hook'),
            Rule('/__engine/1.1/functions/<class_name>/<hook_name>', endpoint='cloud_hook'),
            Rule('/__engine/1/onVerified/<verify_type>', endpoint='on_verified'),
            Rule('/__engine/1.1/onVerified/<verify_type>', endpoint='on_verified'),
            Rule('/__engine/1.1/functions/_User/onLogin', endpoint='on_login'),
            Rule('/__engine/1/functions/_ops/metadatas', endpoint='ops_meta_data'),
            Rule('/__engine/1.1/functions/_ops/metadatas', endpoint='ops_meta_data'),

            Rule('/1/functions/<func_name>', endpoint='cloud_function'),
            Rule('/1.1/functions/<func_name>', endpoint='cloud_function'),
            Rule('/1/functions/BigQuery/<event>', endpoint='on_bigquery'),
            Rule('/1.1/functions/BigQuery/<event>', endpoint='on_bigquery'),
            Rule('/1/functions/<class_name>/<hook_name>', endpoint='cloud_hook'),
            Rule('/1.1/functions/<class_name>/<hook_name>', endpoint='cloud_hook'),
            Rule('/1/onVerified/<verify_type>', endpoint='on_verified'),
            Rule('/1.1/onVerified/<verify_type>', endpoint='on_verified'),
            Rule('/1.1/functions/_User/onLogin', endpoint='on_login'),
            Rule('/1/functions/_ops/metadatas', endpoint='ops_meta_data'),
            Rule('/1.1/functions/_ops/metadatas', endpoint='ops_meta_data'),
        ])

    def __call__(self, environ, start_response):
        self.process_session(environ)
        request = Request(environ)

        response = self.dispatch_request(request)

        return response(environ, start_response)

    @classmethod
    def process_session(cls, environ):
        if environ['_app_params']['session_token'] in (None, ''):
            context.local.user = None
            return

        session_token = environ['_app_params']['session_token']
        user = leancloud.Object.create('_User', session_token=session_token)
        context.local.user = user

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
        except HTTPException, e:
            return e

        params = request.get_data()
        values['params'] = json.loads(params) if params != '' else {}

        try:
            if endpoint == 'cloud_function':
                result = dispatch_cloud_func(**values)
            elif endpoint == 'cloud_hook':
                result = dispatch_cloud_hook(**values)
            elif endpoint == 'on_verified':
                result = dispatch_on_verified(**values)
            elif endpoint == 'on_login':
                result = dispatch_on_login(**values)
            elif endpoint == 'ops_meta_data':
                result = dispatch_ops_meta_data()
            elif endpoint == 'on_bigquery':
                result = dispatch_on_bigquery(**values)
            else:
                raise ValueError    # impossible
            return Response(json.dumps({'result': result}), mimetype='application/json')
        except LeanEngineError, e:
            return Response(
                json.dumps({'code': e.code, 'error': e.message}),
                status=400,
                mimetype='application/json'
            )
        except Exception:
            print traceback.format_exc()
            return Response(
                json.dumps({'code': 141, 'error': 'Cloud Code script had an error.'}),
                status=500,
                mimetype='application/json'
            )


hook_name_mapping = {
    'beforeSave': '__before_save_for_',
    'afterSave': '__after_save_for_',
    'afterUpdate': '__after_update_for_',
    'beforeDelete': '__before_save_for_',
    'afterDelete': '__after_delete_for_',
}

_cloud_codes = {}


def register_cloud_func(func):
    func_name = func.__name__
    if func_name in _cloud_codes:
        raise RuntimeError('cloud function: {0} is already registered'.format(func_name))
    _cloud_codes[func_name] = func


def dispatch_cloud_func(func_name, params):
    func = _cloud_codes.get(func_name)
    if not func:
        raise LeanEngineError(code=404, message="cloud func named '{0}' not found.".format(func_name))

    logger.info("{0} is called!".format(func_name))

    return func(**params)


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

after_update = functools.partial(register_cloud_hook, hook_name='afterUpdate')

before_delete = functools.partial(register_cloud_hook, hook_name='beforeDelete')

after_delete = functools.partial(register_cloud_hook, hook_name='afterDelete')


def dispatch_cloud_hook(class_name, hook_name, params):
    hook_name = hook_name_mapping[hook_name] + class_name
    if hook_name not in _cloud_codes:
        raise NotAcceptable

    obj = leancloud.Object.create(class_name)
    obj._finish_fetch(params['object'], True)

    logger.info("{0}:{1} is called!".format(class_name, hook_name))

    func = _cloud_codes[hook_name]
    if not func:
        raise leancloud.LeanEngineError(code=404, message="cloud hook named '{0}' not found.".format(hook_name))

    return func(obj)


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
    func_name = '__on_login'

    if func_name in _cloud_codes:
        raise RuntimeError('on login is already registered')
    _cloud_codes[func_name] = func


def dispatch_on_login(user):
    func = _cloud_codes.get('__on_login')
    if not func:
        return

    return func(user)


def dispatch_ops_meta_data():
    return _cloud_codes.keys()


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
