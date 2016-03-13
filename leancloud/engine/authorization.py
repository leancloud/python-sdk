# coding: utf-8

import os
import json

from werkzeug.wrappers import Response

from . import utils
from leancloud._compat import to_native

__author__ = 'asaka <lan@leancloud.rocks>'


APP_ID = os.environ.get('LC_APP_ID')
APP_KEY = os.environ.get('LC_APP_KEY')
MASTER_KEY = os.environ.get('LC_APP_MASTER_KEY')


_ENABLE_TEST = False
current_environ = None


class AuthorizationMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if _ENABLE_TEST:
            global current_environ
            current_environ = environ

        self.parse_header(environ)
        app_params = environ['_app_params']
        if not any(app_params.values()):  # all app_params's value is None
            self.parse_body(environ)

        unauth_response = Response(json.dumps({
            'code': 401, 'error': 'Unauthorized.'
        }), status=401, mimetype='application/json')
        if app_params['id'] is None:
            return unauth_response(environ, start_response)
        if (APP_ID == app_params['id']) and (app_params['key'] in [MASTER_KEY, APP_KEY]):
            return self.app(environ, start_response)
        if (APP_ID == app_params['id']) and (app_params['master_key'] == MASTER_KEY):
            return self.app(environ, start_response)

        return unauth_response(environ, start_response)

    @classmethod
    def parse_header(cls, environ):
        request = environ['leanengine.request']

        app_id = request.headers.get('x-avoscloud-application-id')\
            or request.headers.get('x-uluru-application-id')\
            or request.headers.get('x-lc-id')
        app_key = request.headers.get('x-avoscloud-application-key')\
            or request.headers.get('x-uluru-application-key')\
            or request.headers.get('x-lc-key')
        session_token = request.headers.get('x-uluru-session-token')\
            or request.headers.get('x-avoscloud-session-token')\
            or request.headers.get('x-lc-session')
        master_key = request.headers.get('x-uluru-master-key')\
            or request.headers.get('x-avoscloud-master-key')

        if app_key and ',master' in app_key:
            master_key, _ = app_key.split(',')
            app_key = None

        if app_key is None:
            request_sign = request.headers.get('x-avoscloud-request-sign')\
                or request.headers.get('x-lc-sign')
            if request_sign:
                request_sign = request_sign.split(',') if request_sign else []
                sign = request_sign[0].lower()
                timestamp = request_sign[1]
                # key = MASTER_KEY if len(request_sign) == 3 and request_sign[2] == 'master' else APP_KEY
                # if sign == utils.sign_by_key(timestamp, key):
                #     app_key = key
                if (len(request_sign) == 3)\
                        and (request_sign[2] == 'master')\
                        and (sign == utils.sign_by_key(timestamp, MASTER_KEY)):
                    master_key = MASTER_KEY
                elif sign == utils.sign_by_key(timestamp, APP_KEY):
                    app_key = APP_KEY

        environ['_app_params'] = {
            'id': app_id,
            'key': app_key,
            'master_key': master_key,
            'session_token': session_token,
        }

    @classmethod
    def parse_body(cls, environ):
        request = environ['leanengine.request']
        if (not request.content_type) or ('text/plain' not in request.content_type):
            return

        # the JSON object must be str, not 'bytes' for 3.x.
        body = json.loads(to_native(request.data))

        environ['_app_params']['id'] = body.get('_ApplicationId')
        environ['_app_params']['key'] = body.get('_ApplicationKey')
        environ['_app_params']['master_key'] = body.get('_MasterKey')
        environ['_app_params']['session_token'] = body.get('_SessionToken')
