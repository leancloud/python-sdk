# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import utils


class CORSMiddleware(object):
    ALLOW_ORIGIN = utils.to_native("*")
    ALLOW_HEADERS = utils.to_native(
        ", ".join(
            [
                "Content-Type",
                "X-AVOSCloud-Application-Id",
                "X-AVOSCloud-Application-Key",
                "X-AVOSCloud-Application-Production",
                "X-AVOSCloud-Client-Version",
                "X-AVOSCloud-Request-sign",
                "X-AVOSCloud-Session-Token",
                "X-AVOSCloud-Super-Key",
                "X-Requested-With",
                "X-Uluru-Application-Id," "X-Uluru-Application-Key",
                "X-Uluru-Application-Production",
                "X-Uluru-Client-Version",
                "X-Uluru-Session-Token",
                "X-LC-Hook-Key",
                "X-LC-Id",
                "X-LC-Key",
                "X-LC-Prod",
                "X-LC-Session",
                "X-LC-Sign",
                "X-LC-UA",
            ]
        )
    )
    ALLOW_METHODS = utils.to_native(
        ", ".join(["PUT", "GET", "POST", "DELETE", "OPTIONS"])
    )
    MAX_AGE = utils.to_native("86400")

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ["REQUEST_METHOD"] == "OPTIONS":
            start_response(
                utils.to_native("200 OK"),
                [
                    (
                        utils.to_native("Access-Control-Allow-Origin"),
                        environ.get("HTTP_ORIGIN", self.ALLOW_ORIGIN),
                    ),
                    (
                        utils.to_native("Access-Control-Allow-Headers"),
                        self.ALLOW_HEADERS,
                    ),
                    (
                        utils.to_native("Access-Control-Allow-Methods"),
                        self.ALLOW_METHODS,
                    ),
                    (utils.to_native("Access-Control-Max-Age"), self.MAX_AGE),
                ],
            )
            return [utils.to_native("")]
        else:

            def cors_start_response(status, headers, exc_info=None):
                headers.append(
                    (utils.to_native("Access-Control-Allow-Origin"), self.ALLOW_ORIGIN)
                )
                headers.append(
                    (
                        utils.to_native("Access-Control-Allow-Headers"),
                        self.ALLOW_HEADERS,
                    )
                )
                headers.append(
                    (
                        utils.to_native("Access-Control-Allow-Methods"),
                        self.ALLOW_METHODS,
                    )
                )
                headers.append(
                    (utils.to_native("Access-Control-Max-Age"), self.MAX_AGE)
                )
                return start_response(status, headers, exc_info)

            return self.app(environ, cors_start_response)
