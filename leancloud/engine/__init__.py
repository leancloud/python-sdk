# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import json
import warnings

from werkzeug.wrappers import Request
from werkzeug.wrappers import Response
from werkzeug.serving import run_simple

import leancloud
from . import utils
from . import leanengine
from .authorization import AuthorizationMiddleware
from .cookie_session import CookieSessionMiddleware  # noqa: F401
from .cors import CORSMiddleware
from .https_redirect_middleware import HttpsRedirectMiddleware  # noqa: F401
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
from .leanengine import register_on_auth_data
from .leanengine import register_on_verified
from .leanengine import user

__author__ = "asaka <lan@leancloud.rocks>"


class Engine(object):
    """
    LeanEngine middleware.
    """

    def __init__(self, wsgi_app=None, fetch_user=True):
        """
        LeanEngine middleware constructor.

        :param wsgi_app: wsgi callable
        :param fetch_user:
               should fetch user's data from server while prNoneocessing session token.
        :type fetch_user: bool
        """
        self.current = current
        if wsgi_app:
            leanengine.root_engine = self
        self.origin_app = wsgi_app
        self.app = LeanEngineApplication(fetch_user=fetch_user)
        self.cloud_app = context.local_manager.make_middleware(
            CORSMiddleware(AuthorizationMiddleware(self.app))
        )

    def __call__(self, environ, start_response):
        request = Request(environ)
        environ[
            "leanengine.request"
        ] = request  # cache werkzeug request for other middlewares

        if request.path in ("/__engine/1/ping", "/__engine/1.1/ping/"):
            start_response(
                utils.to_native("200 OK"),
                [
                    (
                        utils.to_native("Content-Type"),
                        utils.to_native("application/json"),
                    )
                ],
            )
            version = sys.version_info
            return Response(
                json.dumps(
                    {
                        "version": leancloud.__version__,
                        "runtime": "cpython-{0}.{1}.{2}".format(
                            version.major, version.minor, version.micro
                        ),
                    }
                )
            )(environ, start_response)
        if request.path.startswith("/__engine/"):
            return self.cloud_app(environ, start_response)
        if request.path.startswith("/1/functions") or request.path.startswith(
            "/1.1/functions"
        ):
            return self.cloud_app(environ, start_response)
        if request.path.startswith("/1/call") or request.path.startswith("/1.1/call"):
            return self.cloud_app(environ, start_response)
        return self.origin_app(environ, start_response)

    def wrap(self, wsgi_app):
        if leanengine.root_engine:
            raise RuntimeError("It's forbidden that overwriting wsgi_func.")
        leanengine.root_engine = self
        self.origin_app = wsgi_app
        return self

    def register(self, engine):
        if not isinstance(engine, Engine):
            raise TypeError("Please specify an Engine instance")
        self.app.update_cloud_codes(engine.app.cloud_codes)

    def define(self, *args, **kwargs):
        return register_cloud_func(self.app.cloud_codes, *args, **kwargs)

    def on_verified(self, *args, **kwargs):
        return register_on_verified(self.app.cloud_codes, *args, **kwargs)

    def on_login(self, *args, **kwargs):
        return register_on_login(self.app.cloud_codes, *args, **kwargs)

    def on_auth_data(self, *args, **kwargs):
        return register_on_auth_data(self.app.cloud_codes, *args, **kwargs)

    def on_bigquery(self, *args, **kwargs):
        warnings.warn(
            "on_bigquery is deprecated, please use on_insight instead",
            leancloud.LeanCloudWarning,
        )
        return register_on_bigquery(self.app.cloud_codes, *args, **kwargs)

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

    def start(self):
        from gevent.pywsgi import WSGIServer

        if not hasattr(leancloud, "APP_ID"):
            APP_ID = os.environ["LEANCLOUD_APP_ID"]
            APP_KEY = os.environ["LEANCLOUD_APP_KEY"]
            MASTER_KEY = os.environ["LEANCLOUD_APP_MASTER_KEY"]
            HOOK_KEY = os.environ["LEANCLOUD_APP_HOOK_KEY"]
            PORT = int(os.environ.get("LEANCLOUD_APP_PORT"))
            leancloud.init(
                APP_ID, app_key=APP_KEY, master_key=MASTER_KEY, hook_key=HOOK_KEY
            )

        def application(environ, start_response):
            start_response(
                "200 OK".encode("utf-8"),
                [("Content-Type".encode("utf-8"), "text/plain".encode("utf-8"))],
            )
            return "This is a LeanEngine application."

        class NopLogger(object):
            def write(self, s):
                pass

        app = self.wrap(application)
        self.server = WSGIServer(("", PORT), app, log=NopLogger())
        print("LeanEngine Cloud Functions app is running, port:", PORT)
        self.server.serve_forever()

    def stop(self):
        self.server.stop()


__all__ = ["user", "Engine", "LeanEngineError"]
