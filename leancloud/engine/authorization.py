# coding: utf-8

import os
import json

from werkzeug.wrappers import Request
from werkzeug.wrappers import Response

import utils

__author__ = 'asaka <lan@leancloud.rocks>'


APP_ID = os.environ.get('LC_APP_ID')
APP_KEY = os.environ.get('LC_APP_KEY')
MASTER_KEY = os.environ.get('LC_MASTER_KEY')


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

        unauth_response = Response(json.dumps({'code': 401, 'error': 'Unauthorized.'}), status=401, mimetype='application/json')
        app_params = environ['_app_params']
        if app_params['id'] is None:
            return unauth_response(environ, start_response)
        if (APP_ID == app_params['id']) and (app_params['key'] in [MASTER_KEY, APP_KEY]):
            return self.app(environ, start_response)

        return unauth_response(environ, start_response)

    @classmethod
    def parse_header(cls, environ):
        request = Request(environ)

        app_id = request.headers.get('x-avoscloud-application-id') or request.headers.get('x-uluru-application-id')
        app_key = request.headers.get('x-avoscloud-application-key') or request.headers.get('x-uluru-application-key')
        session_token = request.headers.get('x-uluru-session-token') or request.headers.get('x-avoscloud-session-token')

        if app_key is None:
            request_sign = request.headers.get('x-avoscloud-request-sign')
            if request_sign:
                request_sign = request_sign.split(',') if request_sign else []
                sign = request_sign[0].lower()
                timestamp = request_sign[1]
                key = MASTER_KEY if len(request_sign) == 3 and request_sign[2] == 'master' else APP_KEY
                if sign == utils.sign_by_key(timestamp, key):
                    app_key = key

        environ['_app_params'] = {
            'id': app_id,
            'key': app_key,
            'session_token': session_token,
        }
