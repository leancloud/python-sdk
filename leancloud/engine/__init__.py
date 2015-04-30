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


class LeanEngine(object):
    def __init__(self, wsgi_app):
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


def init(app):
    return LeanEngine(app)


cloud_func = register_cloud_func
cloud_hook = register_cloud_hook
on_verified = register_on_verified
run = run_simple


__all__ = [
    'wrap',
    'user',
    'register_cloud_func',
    'register_cloud_hook',
    'register_on_verified',
    'on_verified',
    'cloud_func',
    'cloud_hook',
    'run',
    'before_save',
    'after_save',
    'after_update',
    'before_delete',
    'after_delete',
    'LeanEngineError'
]
