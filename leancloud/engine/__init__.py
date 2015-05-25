# coding: utf-8

from werkzeug.wrappers import Request
from werkzeug.serving import run_simple

import context
from .authorization import AuthorizationMiddleware
from .leanengine import LeanEngineApplication
from .leanengine import LeanEngineError
from .leanengine import register_cloud_func
from .leanengine import register_cloud_hook
from .leanengine import register_on_verified
from .leanengine import before_save
from .leanengine import after_save
from .leanengine import after_update
from .leanengine import before_delete
from .leanengine import after_delete
from .leanengine import user

__author__ = 'asaka <lan@leancloud.rocks>'


class Engine(object):
    def __init__(self, wsgi_app):
        self.current_user = user
        self.origin_app = wsgi_app
        self.cloud_app = context.local_manager.make_middleware(AuthorizationMiddleware(LeanEngineApplication()))

    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.path in ('/1/ping', '/1/ping/'):
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return ['pong']
        if request.path.startswith('/1/functions') or request.path.startswith('/1.1/functions'):
            return self.cloud_app(environ, start_response)
        return self.origin_app(environ, start_response)

    define = staticmethod(register_cloud_func)
    on_verified = staticmethod(register_on_verified)
    before_save = staticmethod(before_save)
    after_save = staticmethod(after_save)
    after_update = staticmethod(after_update)
    before_delete = staticmethod(before_delete)
    after_delete = staticmethod(after_delete)

    run = staticmethod(run_simple)


__all__ = [
    'user',
    'Engine',
    'LeanEngineError'
]
