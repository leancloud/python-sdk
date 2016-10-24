# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from werkzeug import http
from werkzeug.wrappers import Request
from werkzeug.contrib.securecookie import SecureCookie

from leancloud.user import User


__author__ = 'asaka <lan@leancloud.rocks>'


class CookieSessionMiddleware(object):
    def __init__(self, app, secret, name='leancloud:session', exluded_paths=None, fetch_user=False):
        if not secret:
            raise RuntimeError('secret is required')
        self.fetch_user = fetch_user
        self.secret = secret
        self.app = app
        self.name = name
        self.exluded_paths = [
            '/__engine/',
            '/1/functions/',
            '/1.1/functions/',
            '/1/call/',
            '/1.1/call/',
        ]
        if exluded_paths:
            self.exluded_paths += exluded_paths

    def __call__(self, environ, start_response):
        self.pre_process(environ)
        def new_start_response(status, response_headers):
            self.post_process(response_headers)
            return start_response(status, response_headers)
        return self.app(environ, new_start_response)

    def pre_process(self, environ):
        request = Request(environ)
        for prefix in self.exluded_paths:
            if request.path.startswith(prefix):
                return

        cookie = request.cookies.get(self.name)
        if not cookie:
            return

        session = SecureCookie.unserialize(cookie, self.secret)

        if not self.fetch_user:
            user = User()
            user._session_token = session['session_token']
            user.id = session['uid']
            User.set_current(user)
        else:
            user = User.become(session['session_token'])
            User.set_current(user)


    def post_process(self, headers):
        user = User.get_current()
        if not user:
            return
        cookie = SecureCookie({
            'uid': user.id,
            'session_token': user.get_session_token(),
        }, self.secret)
        raw = http.dump_cookie(self.name, cookie.serialize())
        headers.append((b'Set-Cookie', raw))
