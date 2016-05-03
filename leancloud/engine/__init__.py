# coding: utf-8

import sys
import json

from werkzeug.wrappers import Request
from werkzeug.serving import run_simple

import leancloud
from . import context
from .authorization import AuthorizationMiddleware
from .cors import CORSMiddleware
from .leanengine import LeanEngineApplication
from .leanengine import LeanEngineError
from .leanengine import register_cloud_func
from .leanengine import register_on_verified
from .leanengine import register_on_login
from .leanengine import before_save
from .leanengine import after_save
from .leanengine import before_update
from .leanengine import after_update
from .leanengine import before_delete
from .leanengine import after_delete
from .leanengine import user
from .leanengine import register_on_bigquery

__author__ = 'asaka <lan@leancloud.rocks>'


class Engine(object):
    def __init__(self, wsgi_app):
        self.current_user = user
        self.origin_app = wsgi_app
        self.cloud_app = context.local_manager.make_middleware(CORSMiddleware(AuthorizationMiddleware(LeanEngineApplication())))

    def __call__(self, environ, start_response):
        request = Request(environ)
        environ['leanengine.request'] = request  # cache werkzeug request for other middlewares

        if request.path in ('/__engine/1/ping', '/__engine/1.1/ping/'):
            start_response('200 OK', [('Content-Type', 'application/json')])
            version = sys.version_info
            return [json.dumps({
                'version': leancloud.__version__,
                'runtime': 'cpython-{0}.{1}.{2}'.format(version.major, version.minor, version.micro)
            })]
        if request.path.startswith('/__engine/'):
            return self.cloud_app(environ, start_response)
        if request.path.startswith('/1/functions') or request.path.startswith('/1.1/functions'):
            return self.cloud_app(environ, start_response)
        if request.path.startswith('/1/call') or request.path.startswith('/1.1/call'):
            return self.cloud_app(environ, start_response)
        return self.origin_app(environ, start_response)

    define = staticmethod(register_cloud_func)
    on_verified = staticmethod(register_on_verified)
    on_login = staticmethod(register_on_login)
    before_save = staticmethod(before_save)
    after_save = staticmethod(after_save)
    before_update = staticmethod(before_update)
    after_update = staticmethod(after_update)
    before_delete = staticmethod(before_delete)
    after_delete = staticmethod(after_delete)
    on_bigquery = staticmethod(register_on_bigquery)

    run = staticmethod(run_simple)


__all__ = [
    'user',
    'Engine',
    'LeanEngineError'
]
