# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .._compat import PY3

import os


from werkzeug.wrappers import Request
from werkzeug.utils import redirect

__author__ = 'asaka <lan@leancloud.rocks>'


is_prod = True if os.environ.get('LEANCLOUD_APP_ENV') == 'production' else False

class HttpsRedirectMiddleware(object):
    def __init__(self, wsgi_app):
        self.origin_app = wsgi_app

    def __call__(self, environ, start_response):
        request = Request(environ)
        if is_prod and request.headers.get('X-Forwarded-Proto') != 'https':
            url = 'https://{0}{1}'.format(request.host, request.path)
            if request.query_string:
                if PY3:
                    url += '?{0}'.format(request.query_string.decode())
                else:
                    url += '?{0}'.format(request.query_string)
            return redirect(url)(environ, start_response)

        return self.origin_app(environ, start_response)
