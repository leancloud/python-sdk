# coding: utf-8

import sys
import json
import warnings

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
    def __init__(self, wsgi_app):
        self.current = current
        self.origin_app = wsgi_app
        self.cloud_app = context.local_manager.make_middleware(CORSMiddleware(AuthorizationMiddleware(LeanEngineApplication())))

    def __call__(self, environ, start_response):
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

    @property
    def current_user(self):
        warnings.warn('Engine.current_user is deprecated, please use Engine.current.user instead', leancloud.LeanCloudWarning)
        return user

    @staticmethod
    def on_bigquery(*args, **kwargs):
        warnings.warn('on_bigquery is deprecated, please use on_insight instead', leancloud.LeanCloudWarning)
        return register_on_bigquery(*args, **kwargs)

    def define(self, *args, **kwargs):
        return register_cloud_func(*args, **kwargs)

    def on_verified(self, *args, **kwargs):
        return register_on_verified(*args, **kwargs)

    def on_login(self, *args, **kwargs):
        return register_on_login(*args, **kwargs)

    def before_save(self, *args, **kwargs):
        return before_save(*args, **kwargs)

    def after_save(self, *args, **kwargs):
        return after_save(*args, **kwargs)

    def before_update(self, *args, **kwargs):
        return before_update(*args, **kwargs)

    def after_update(self, *args, **kwargs):
        return after_update(*args, **kwargs)

    def before_delete(self, *args, **kwargs):
        return before_delete(*args, **kwargs)

    def after_delete(self, *args, **kwargs):
        return after_delete(*args, **kwargs)

    def on_insight(self, *args, **kwargs):
        return register_on_bigquery(*args, **kwargs)

    def run(self, *args, **kwargs):
        return run_simple(*args, **kwargs)


__all__ = [
    'user',
    'Engine',
    'LeanEngineError'
]
