# coding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import time

import requests
from wsgi_intercept import add_wsgi_intercept
from wsgi_intercept import remove_wsgi_intercept
from wsgi_intercept import requests_intercept

from leancloud import user as user_module
from leancloud.engine.cookie_session import CookieSessionMiddleware


HOST, PORT = 'localhost', 80
URL = 'http://{}:{}/'.format(HOST, PORT)

FAKE_USER_DATA = {
  'sessionToken': 'qmdj8pdidnmyzp0c7yqil91oc',
  'updatedAt': '2015-07-14T02:31:50.100Z',
  'phone': '18612340000',
  'objectId': '55a47496e4b05001a7732c5f',
  'username': 'fool',
  'createdAt': '2015-07-14T02:31:50.100Z',
  'emailVerified': False,
  'mobilePhoneVerified': False,
}


def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b'hello!']


def setup():
    requests_intercept.install()


def teardown():
    requests_intercept.uninstall()


def test_cookie_session_middleware():
    user = user_module.User()
    user._update_data(FAKE_USER_DATA)
    user_module.thread_locals.current_user = user

    app = CookieSessionMiddleware(application, b'wtf!')
    add_wsgi_intercept(HOST, PORT, lambda: app)

    response = requests.get(URL)
    assert response.cookies['leancloud:session']

    del user_module.thread_locals.current_user

    requests.get(URL, cookies=response.cookies)
    current = user_module.User.get_current()
    assert current.id == user.id
    assert current.get_session_token() == user.get_session_token()
    assert not current._attributes
    remove_wsgi_intercept()
