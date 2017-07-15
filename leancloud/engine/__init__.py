# coding: utf-8

import sys
import json

from werkzeug.wrappers import Request
from werkzeug.wrappers import Response
from werkzeug.serving import run_simple

import leancloud
from .authorization import AuthorizationMiddleware
from .cookie_session import CookieSessionMiddleware
from .cors import CORSMiddleware
from .https_redirect_middleware import HttpsRedirectMiddleware
from .leanengine import LeanEngineApplication
from .leanengine import LeanEngineError
from .leanengine import after_delete
from .leanengine import after_save
from .leanengine import after_update
from .leanengine import before_delete
from .leanengine import before_save
from .leanengine import before_update
from .leanengine import context
from .leanengine import current
from .leanengine import register_cloud_func
from .leanengine import register_on_bigquery
from .leanengine import register_on_login
from .leanengine import register_on_verified
from .leanengine import user

__author__ = 'asaka <lan@leancloud.rocks>'


class Engine(object):
    def __init__(self, wsgi_app=None):
        self.current = current
        self.origin_app = wsgi_app
        self.app = LeanEngineApplication()
        self.cloud_app = context.local_manager.make_middleware(CORSMiddleware(AuthorizationMiddleware(self.app)))

    def __call__(self, environ, start_response):
        if not self.origin_app:
            raise ValueError("Please use engine.wrap to wrap wsgi function")
        request = Request(environ)
        environ['leanengine.request'] = request  # cache werkzeug request for other middlewares

        if request.path in ('/__engine/1/ping', '/__engine/1.1/ping/'):
            start_response('200 OK', [('Content-Type', 'application/json')])
            version = sys.version_info
            return Response(json.dumps({
                'version': leancloud.__version__,
                'runtime': 'cpython-{0}.{1}.{2}'.format(version.major, version.minor, version.micro)
            }))(environ, start_response)
        if request.path.startswith('/__engine/'):
            return self.cloud_app(environ, start_response)
        if request.path.startswith('/1/functions') or request.path.startswith('/1.1/functions'):
            return self.cloud_app(environ, start_response)
        if request.path.startswith('/1/call') or request.path.startswith('/1.1/call'):
            return self.cloud_app(environ, start_response)
        return self.origin_app(environ, start_response)

    def wrap(self, wsgi_app):
        self.origin_app = wsgi_app

    def register(self, engine):
        if not isinstance(engine, Engine):
            raise ValueError("Please specify an Engine instance")
        self.app.update_cloud_codes(engine.app.cloud_codes)

    def define(self, *args, **kwargs):
        return register_cloud_func(self.app.cloud_codes, *args, **kwargs)

    def on_verified(self, *args, **kwargs):
        return register_on_verified(self.app.cloud_codes, *args, **kwargs)

    def on_login(self, *args, **kwargs):
        return register_on_login(self.app.cloud_codes, *args, **kwargs)

    def before_save(self, *args, **kwargs):
        return before_save(self.app.cloud_codes, *args, **kwargs)

    def after_save(self, *args, **kwargs):
        return after_save(self.app.cloud_codes, *args, **kwargs)

    def before_update(self, *args, **kwargs):
        return before_update(self.app.cloud_codes, *args, **kwargs)

    def after_update(self, *args, **kwargs):
        return after_update(self.app.cloud_codes, *args, **kwargs)

    def before_delete(self, *args, **kwargs):
        return before_delete(self.app.cloud_codes, *args, **kwargs)

    def after_delete(self, *args, **kwargs):
        return after_delete(self.app.cloud_codes, *args, **kwargs)

    def on_insight(self, *args, **kwargs):
        return register_on_bigquery(self.app.cloud_codes, *args, **kwargs)

    def run(self, *args, **kwargs):
        return run_simple(*args, **kwargs)


__all__ = [
    'user',
    'Engine',
    'LeanEngineError'
]
